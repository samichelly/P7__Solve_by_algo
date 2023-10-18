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

    # second_max_profit = 0

    if max_profit >= second_max_profit:
        return best_combination
    else:
        return best_combination_without_last_action + optional_combination


"""
def find_best_combination_optimized(actions_data, budget_limit):
    # Create new column ratio (profit/price) and sort on this column
    actions_data = assign_profit_price_ratio(actions_data)
    actions_data = sort_by_profit_price_ratio(actions_data)

    # Init variables and for actions, current_budget and max_profit
    best_combination = []
    current_budget = 0
    max_profit = 0
    optional_actions = []  # To stock alternative actions

    # Add actions until current_budget is under or equal to budget_limit
    for action in actions_data:
        if is_within_budget(current_budget, action):
            add_action_to_combination(best_combination, action)
            update_budget_and_profit(current_budget, max_profit, action)
        # If current_budget is over, add some others actions (10 for instance) in new list
        else:
            if can_add_as_optional_action(optional_actions):
                add_action_to_optional_list(optional_actions, action)

    # Stockez la dernière action, calculez le budget sans elle et trouvez la combinaison optionnelle
    best_combination_without_last_action = remove_last_action(best_combination)
    last_action = get_last_action(best_combination)
    budget_without_last = calculate_budget_without_last_action(current_budget, last_action)
    max_profit_without_last = calculate_max_profit_without_last_action(max_profit, last_action)
    optional_combination = create_empty_optional_combination()

    # Without last_action calculate and add to optionnal_combination until current_budget is over
    for action in optional_actions:
        if can_add_action_to_budget(budget_without_last, action):
            add_action_to_combination(optional_combination, action)
            update_budget_without_last(budget_without_last, action)

    # Calculate profit with optionnal_actions
    second_max_profit = calculate_second_max_profit(max_profit_without_last, optional_combination)


    if is_max_profit_better(max_profit, second_max_profit): # If max_profit (first calcul) is better, return best_combination
        return best_combination
    else: # Else, return second combination of actions
        return best_combination_without_last_action + optional_combination
"""


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
    print("Total cost:", sum(action["price"] for action in best_combination))
    print("Total profit:", sum(action["profit"] for action in best_combination))

    execution_time = round(end_time - start_time, 2)
    print("Execution time:", execution_time, "seconds")
    return best_combination


if __name__ == "__main__":
    best_combination = main()
    export_to_csv(best_combination, "result_optimized.csv")
