import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict
from itertools import product

EXPECTED_MONOTONIC_FUNCTIONS = [
    (0, 0, 1, 0, 0, 0, 0, 0, 0),
    (0, 1, 1, 0, 0, 0, 0, 0, 0),
    (0, 0, 1, 0, 0, 1, 0, 0, 0),
    (0, 1, 1, 0, 0, 1, 0, 0, 0),
    (0, 0, 1, 0, 0, 1, 0, 0, 1),
    (0, 1, 1, 0, 0, 1, 0, 0, 1),
    (0, 1, 1, 0, 1, 1, 0, 0, 0),
    (0, 1, 1, 0, 1, 1, 0, 0, 1),
    (0, 1, 1, 0, 1, 1, 0, 1, 1),
    (1, 1, 1, 0, 0, 0, 0, 0, 0),
    (1, 1, 1, 0, 0, 1, 0, 0, 0),
    (1, 1, 1, 0, 1, 1, 0, 0, 0),
    (1, 1, 1, 1, 1, 1, 0, 0, 0),
    (1, 1, 1, 0, 0, 1, 0, 0, 1),
    (1, 1, 1, 0, 1, 1, 0, 0, 1),
    (1, 1, 1, 1, 1, 1, 0, 0, 1),
    (1, 1, 1, 0, 1, 1, 0, 1, 1),
    (1, 1, 1, 1, 1, 1, 0, 1, 1),
]

EXPECTED_NUM_MONOTONIC_FUNCTIONS = len(EXPECTED_MONOTONIC_FUNCTIONS)


@dataclass
class GenNetwork:
    num_of_open_activators: int
    num_of_open_repressor: int
    gen_id: str  

    def __post_init__(self):
        if not (0 <= self.num_of_open_activators <= 2):
            raise ValueError("num_of_open_activators must be between 0 and 2.")
        if not (0 <= self.num_of_open_repressor <= 2):
            raise ValueError("num_of_open_repressor must be between 0 and 2.")


def find_all_possible_networks() -> List[GenNetwork]:
    all_networks = []
    gen_id = 1  

    for num_of_open_repressor in [0, 1, 2]:
        for num_of_open_activators in [0, 1, 2]:
            all_networks.append(
                GenNetwork(
                    num_of_open_activators, num_of_open_repressor, str(gen_id)
                )  
            )
            gen_id += 1 

    return all_networks


def generate_output_combinations(
    networks: List[GenNetwork],
) -> Dict[str, Dict[str, int]]:
    num_networks = len(networks)

    all_combinations = list(product([0, 1], repeat=num_networks))

    output_dict = {}

    for idx, combination in enumerate(all_combinations):
        func_key = f"func{idx+1}"
        output_dict[func_key] = {}
        for network, output in zip(networks, combination):
            output_dict[func_key][network.gen_id] = output

    return output_dict


def is_monotonic(networks: List[GenNetwork], combination: Dict[str, int]) -> bool:
    # if all outputs are the same, return False
    if len(set(combination.values())) == 1:
        return False

    for net1 in networks:
        for net2 in networks:
            if net1 == net2:
                continue

            output1 = combination[net1.gen_id]
            output2 = combination[net2.gen_id]

            # Check monotonicity condition for activators
            if (
                net1.num_of_open_activators >= net2.num_of_open_activators
                and net1.num_of_open_repressor <= net2.num_of_open_repressor
            ):
                if (
                    output1 < output2
                ):  # Increasing activators should not decrease the output
                    return False

            # Check monotonicity condition for repressors
            if (
                net1.num_of_open_activators <= net2.num_of_open_activators
                and net1.num_of_open_repressor >= net2.num_of_open_repressor
            ):
                if (
                    output1 > output2
                ):  # Increasing repressors should not increase the output
                    return False

    return True


def filter_monotonic_functions(
    networks: List[GenNetwork], output_dict: Dict[str, Dict[str, int]]
) -> Dict[str, Dict[str, int]]:
    """
    Filter the output dictionary to keep only monotonic functions.
    """
    monotonic_dict = {}

    for func_key, combination in output_dict.items():
        if is_monotonic(networks, combination):
            monotonic_dict[func_key] = combination

    return monotonic_dict


def plot_monotonic_functions(df: pd.DataFrame):
    plt.figure(figsize=(10, 6))

    plt.imshow(df, cmap="Reds", aspect="auto")

    plt.xlabel("Network Configuration (Open Activator, Repressor)")
    plt.ylabel("Monotonic Function")
    plt.title("Monotonic Functions Visualization")

    plt.xticks(ticks=range(len(df.columns)), labels=df.columns, rotation=45, ha="right")

    plt.yticks(ticks=range(len(df.index)), labels=range(1, len(df.index) + 1))

    for y in range(df.shape[0] + 1):
        plt.axhline(y - 0.5, color="black", linewidth=2)

    for x in range(df.shape[1] + 1):
        plt.axvline(x - 0.5, color="black", linewidth=2)
        
    plt.savefig("plot.png")

    plt.show()


def test_monotonic_functions():
    # arrange
    expected_monotonic_functions = EXPECTED_MONOTONIC_FUNCTIONS
    expected_num_monotonic_functions = EXPECTED_NUM_MONOTONIC_FUNCTIONS

    # act
    gen_networks = find_all_possible_networks()
    output_combinations = generate_output_combinations(gen_networks)
    monotonic_functions = filter_monotonic_functions(gen_networks, output_combinations)

    # assert
    monotonic_functions_list = [
        tuple(val.values()) for val in monotonic_functions.values()
    ]
    assert expected_num_monotonic_functions == len(monotonic_functions_list)

    for func in expected_monotonic_functions:
        assert func in monotonic_functions_list

    print("All tests passed successfully!")    


def main():
    test_monotonic_functions()

    gen_networks = find_all_possible_networks()
    output_combinations = generate_output_combinations(gen_networks)
    monotonic_functions = filter_monotonic_functions(gen_networks, output_combinations)

    num_monotonic_functions = len(monotonic_functions)
    print(f"Number of monotonic functions: {num_monotonic_functions}")

    df = pd.DataFrame(monotonic_functions).T
    df.index = range(1, len(df) + 1)
    df.columns = [
        (gen_networks[i].num_of_open_activators, gen_networks[i].num_of_open_repressor)
        for i in range(len(gen_networks))
    ]
    print("\nList of Monotonic Functions:")
    print(df)
    
    df.to_csv("monotonic_functions.csv")

    plot_monotonic_functions(df)


if __name__ == "__main__":
    main()
