import time
import pandas as pd
import argparse

BUDGET_MAX = 50


def load_data(data_file):
    """
    Load data from a CSV file and return a DataFrame.
    :param data_file: The path to the CSV file.
    :return: The DataFrame containing the data.
    """
    data = pd.read_csv(data_file, sep=",")
    return data


def clean_data(actions_data):
    """
    Remove rows with negative or zero price or profit from the data.
    :param actions_data: DataFrame with data on investment actions.
    :return: Cleaned DataFrame with valid actions.
    """
    cleaned_data = actions_data[
        (actions_data["price"] > 0) & (actions_data["profit"] > 0)
    ]
    print("Number of valid actions:", len(cleaned_data))
    return cleaned_data


def find_best_combination_optimized(actions_data, budget_limit):
    """
    Find the best investment action combination using an optimized approach.
    :param actions_data: DataFrame with data on investment actions.
    :param budget_limit: The maximum budget for investment.
    :return: List of the best actions to purchase.
    """
    # Add a new column for profit/price ratio and sort by the ratio in descending order
    actions_data = actions_data.assign(
        profit_price_ratio=actions_data["profit"] / actions_data["price"]
    )
    actions_data = actions_data.sort_values(by="profit_price_ratio", ascending=False)

    # Initialize lists to store actions and calculate the budget and profit
    best_combination = []
    current_budget = 0
    max_profit = 0
    optional_actions = []  # List to store alternative actions

    # Iterate through the actions and add them to the combination if within the budget
    for _, action in actions_data.iterrows():
        if current_budget + action["price"] <= budget_limit:
            best_combination.append(action)
            current_budget += action["price"]
            max_profit += action["profit"]
        else:
            if (
                len(optional_actions) < 10
            ):  # Limit the number of alternative actions to 10
                optional_actions.append(action)

    # Store the last action, calculate the budget without it, and find the optional combination
    best_combination_without_last_action = best_combination[:-1]
    last_action = best_combination[-1]
    budget_without_last = current_budget - last_action["price"]
    max_profit_without_last = max_profit - last_action["profit"]
    optional_combination = []

    for action in optional_actions:
        if budget_without_last + action["price"] <= budget_limit:
            optional_combination.append(action)
            budget_without_last += action["price"]

    # Calculate the profit of the optional combination
    second_max_profit = max_profit_without_last + sum(
        action["profit"] for action in optional_combination
    )

    if max_profit >= second_max_profit:
        return best_combination
    else:
        return best_combination_without_last_action + optional_combination


def main():
    parser = argparse.ArgumentParser(
        description="Find the best investment combination from a CSV file."
    )
    parser.add_argument(
        "csv_file", type=str, help="Path to the CSV file with investment data"
    )
    args = parser.parse_args()

    data = load_data(args.csv_file)
    cleaned_data = clean_data(data)
    start_time = time.time()
    best_combination = find_best_combination_optimized(cleaned_data, BUDGET_MAX)
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
