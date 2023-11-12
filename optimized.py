import time
import argparse
import numpy as np
import pandas as pd

BUDGET_DEFAUT = 100


def load_data(data_file):
    """
    Load data from a CSV file and return a DataFrame.
    :param data_file: The path to the CSV file.
    :return: The DataFrame containing the data.
    """
    data = pd.read_csv(data_file, sep=",")
    return data


def sort_by_ratio(cleaned_data):
    # Add a new column for profit/price ratio and sort by the ratio in descending order
    cleaned_data = cleaned_data.assign(
        profit_price_ratio=cleaned_data["profit"] / cleaned_data["price"]
    )
    return cleaned_data.sort_values(by="profit_price_ratio", ascending=False)


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
    return sort_by_ratio(cleaned_data)


def find_best_combination_optimized(actions_data, budget_limit, options=True):
    """
    Find the best investment action combination using an optimized approach.
    :param actions_data: DataFrame with data on investment actions.
    :param budget_limit: The maximum budget for investment.
    :return: List of the best actions to purchase.
    """

    # Initialize lists to store actions and calculate the budget and profit
    best_combination = []
    current_budget = 0
    max_profit = 0
    optional_actions = []  # List to store alternative actions

    # Iterate through the actions and add them to the combination if within the budget
    for index, action in actions_data.iterrows():
        if current_budget + action["price"] <= budget_limit:
            best_combination.append(action)
            current_budget += action["price"]
            max_profit += action["profit"]
        else:
            if (
                len(optional_actions) < 10
            ):  # Limit the number of alternative actions to 10
                optional_actions.append(action)
    if options is False:
        return best_combination

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


def find_best_combination_dynamic_prog(actions, budget, precision, decimal_to_apply):
    actions["price"] = (actions["price"] * precision).round(decimals=decimal_to_apply)
    budget_dynamic = budget * precision
    num_actions = len(actions)
    matrix = np.zeros((num_actions + 1, budget_dynamic + 1), dtype=int)

    for i in range(1, num_actions + 1):
        for j in range(budget_dynamic + 1):
            if actions.iloc[i - 1]["price"] > j:
                matrix[i][j] = matrix[i - 1][j]
            else:
                matrix[i][j] = max(
                    matrix[i - 1][j],
                    matrix[i - 1][j - int(actions.iloc[i - 1]["price"])]
                    + int(actions.iloc[i - 1]["profit"]),
                )

    actions_retenues = []
    i, j = num_actions, budget_dynamic
    while i > 0 and j > 0:
        if matrix[i][j] != matrix[i - 1][j]:
            actions_retenues.append(actions.iloc[i - 1])
            j -= int(actions.iloc[i - 1]["price"])
        i -= 1

    for i in actions_retenues:
        i["price"] = i["price"] / precision

    return actions_retenues


def export_to_csv(data, filename):
    """
    Export the selected actions to a CSV file.
    :param data: List of selected actions.
    :param filename: The name of the CSV file to export.
    """
    # Create a DataFrame from the list of selected actions
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(filename, index=False)


def get_user_budget():
    user_budget = input("\nDefine your budget (press Enter for default): ")
    return int(user_budget) if user_budget else BUDGET_DEFAUT


def get_precision(cleaned_data):
    count_decimals = lambda x: len(str(x).split(".")[1]) if "." in str(x) else 0
    max_decimals = cleaned_data["price"].apply(count_decimals).max()

    while True:
        print(
            f"\nYour current precision is {max_decimals}. "
            "Do you want to reduce the precision?"
        )
        print("Your choice can't be higher than the current precision.")
        print("(Higher Precision = Accurate Profit = Longer Processing Time)")
        print("0 - 0 decimal\n1 - 1 decimal\n2 - 2 decimals\n")

        decimal = int(input())

        if decimal >= 0 and decimal <= max_decimals:
            return 10**decimal, decimal
        else:
            print("Invalid choice. Please choose a valid precision.")


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

    SET_BUDGET = get_user_budget()

    calcul_method = int(
        input(
            "\nDefine your calculation method\n"
            "-1 Dynamic\n-2 Optimized without options\n-3 Optimized with options\n"
        )
    )

    if calcul_method == 1:
        precision, decimal_to_apply = get_precision(cleaned_data)
    elif calcul_method not in {2, 3}:
        print("Invalid choice")
        return

    start_time = time.time()
    print("Calculating the best combination...")

    if calcul_method == 1:
        best_combination = find_best_combination_dynamic_prog(
            cleaned_data, SET_BUDGET, precision, decimal_to_apply
        )
        print("Best combination by dynamic prog :")
    elif calcul_method == 2:
        best_combination = find_best_combination_optimized(
            cleaned_data, SET_BUDGET, options=False
        )
        print("Best combination by optimized without options :")
    elif calcul_method == 3:
        best_combination = find_best_combination_optimized(cleaned_data, SET_BUDGET)
        print("Best combination by optimized with options :")

    end_time = time.time()

    for action in best_combination:
        print(
            action["name"],
            "- Price:",
            round(action["price"], 2),
            "- Profit:",
            action["profit"],
        )
    print("Total cost:", round(sum(action["price"] for action in best_combination), 2))
    print(
        "Total profit:", round(sum(action["profit"] for action in best_combination), 2)
    )

    execution_time = round(end_time - start_time, 2)
    print("Execution time:", execution_time, "seconds")


if __name__ == "__main__":
    main()
