import time
import pandas as pd
from itertools import combinations
import argparse

BUDGET_MAX = 50


def load_data(data_to_read):
    """
    Load data from a CSV file and return a DataFrame.
    :param data_to_read: The path to the CSV file.
    :return: The DataFrame containing the data.
    """
    data = pd.read_csv(data_to_read, sep=",")
    return data


def clean_data(actions_data):
    """
    Clean the data by removing rows with negative or zero price and profit.
    :param actions_data: DataFrame with data on investment actions.
    :return: The cleaned DataFrame.
    """
    cleaned_data = actions_data[
        (actions_data["price"] > 0) & (actions_data["profit"] > 0)
    ]
    print("Number of valid actions :", len(cleaned_data))
    return cleaned_data


def find_best_combination(actions_data, budget_limit):
    """
    Find the best investment action combination using a brute-force approach.
    :param actions_data: DataFrame with data on investment actions.
    :param budget_limit: The maximum budget for investment.
    :return: List of the best actions to purchase.
    """
    best_combination = []
    max_profit = 0

    for r in range(len(actions_data)):
        for combination in combinations(actions_data.iterrows(), r):
            total_price = sum(action[1]["price"] for action in combination)

            if total_price <= budget_limit:
                total_profit = sum(action[1]["profit"] for action in combination)

                if total_profit > max_profit:
                    max_profit = total_profit
                    best_combination = combination

    return [action[1] for action in best_combination]


def main():
    parser = argparse.ArgumentParser(
        description="Find the best investment combination from a CSV file."
    )
    parser.add_argument(
        "csv_file", type=str, help="Path to the CSV file with investment data"
    )
    args = parser.parse_args()

    data = load_data(args.csv_file)
    cleaned_data = clean_data(data)  # Clean the data
    start_time = time.time()
    best_combination = find_best_combination(cleaned_data, BUDGET_MAX)
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
