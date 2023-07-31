import time
import pandas as pd
from itertools import combinations

BUDGET_LAX = 500
CSV_FILE = "data_bruteforce.csv"


def get_data(data_to_read):
    data = pd.read_csv(data_to_read, sep=",")
    print(data)
    return data


def find_best_combination(actions_data, budget_limit):
    # action[1] = Pandas Series du tuple (index Dataframe, Pandas Serie)
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
    data = get_data(CSV_FILE)
    start_time = time.time()
    best_combination = find_best_combination(data, BUDGET_LAX)
    end_time = time.time()

    print("Meilleure combinaison d'actions :")
    for action in best_combination:
        print(
            action["name"], "- Prix :", action["price"], "- Profit :", action["profit"]
        )
    print("Profit total :", sum(action["profit"] for action in best_combination))

    execution_time = end_time - start_time
    print("Temps d'exécution :", execution_time, "secondes")


main()
