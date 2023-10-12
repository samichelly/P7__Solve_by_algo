import time
import pandas as pd
import argparse

BUDGET_MAX = 500


def load_data(data_to_read):
    """
    Load data from a CSV file and return a DataFrame.
    :param data_to_read: The path to the CSV file.
    :return: The DataFrame containing the data.
    """
    data = pd.read_csv(data_to_read, sep=",")
    return data


def find_best_combination_greedy(actions_data, budget_limit):
    """
    Find the best investment action combination using a non-optimized greedy approach.
    :param actions_data: DataFrame with data on investment actions.
    :param budget_limit: The maximum budget for investment.
    :return: List of the best actions to purchase.
    """
    best_combination = []
    current_budget = 0
    max_profit = 0

    for index, action in actions_data.iterrows():
        if current_budget + action["price"] <= budget_limit:
            best_combination.append(action)
            current_budget += action["price"]
            max_profit += action["profit"]

    return best_combination


def find_best_combination_optimized(actions_data, budget_limit):
    """
    Find the best investment action combination using an optimized greedy approach.
    :param actions_data: DataFrame with data on investment actions.
    :param budget_limit: The maximum budget for investment.
    :return: List of the best actions to purchase.
    """
    actions_data = actions_data.assign(
        profit_price_ratio=actions_data["profit"] / actions_data["price"]
    )
    actions_data = actions_data.sort_values(by="profit_price_ratio", ascending=False)

    best_combination = []
    current_budget = 0
    max_profit = 0

    for index, action in actions_data.iterrows():
        if current_budget + action["price"] <= budget_limit:
            best_combination.append(action)
            current_budget += action["price"]
            max_profit += action["profit"]

    return best_combination


def main():
    parser = argparse.ArgumentParser(
        description="Find the best investment combination from a CSV file."
    )
    parser.add_argument(
        "csv_file", type=str, help="Path to the CSV file with investment data"
    )
    parser.add_argument(
        "--optimized", action="store_true", help="Use the optimized greedy algorithm"
    )
    args = parser.parse_args()

    # Load data from the specified CSV file
    data = load_data(args.csv_file)
    start_time = time.time()

    if args.optimized:
        best_combination = find_best_combination_optimized(data, BUDGET_MAX)
    else:
        best_combination = find_best_combination_greedy(data, BUDGET_MAX)

    end_time = time.time()

    print("Best combination of actions:")
    for action in best_combination:
        print(
            action["name"], "- Price:", action["price"], "- Profit:", action["profit"]
        )
    print("Total profit:", sum(action["profit"] for action in best_combination))

    execution_time = round(end_time - start_time, 2)
    print("Execution time:", execution_time, "seconds")


if __name__ == "__main__":
    main()
