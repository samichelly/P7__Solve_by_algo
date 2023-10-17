import time
import pandas as pd
import argparse

BUDGET_MAX = 500


def load_data(data_to_read):
    data = pd.read_csv(data_to_read, sep=",")
    return data


def clean_data(actions_data):
    # Remove rows with negative or zero price and profit
    cleaned_data = actions_data[
        (actions_data["price"] > 0) & (actions_data["profit"] > 0)
    ]
    print("Number of valid actions, ", len(cleaned_data))
    return cleaned_data


def find_best_combination_optimized(actions_data, budget_limit):
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
    args = parser.parse_args()

    data = load_data(args.csv_file)
    cleaned_data = clean_data(data)  # Clean the data
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
