import json
import os

import stats

available_stats = [
    stats.RatingProgress,
    stats.AccurateWinRateByRating,
    stats.OpponentHeroDistribution,
    stats.WinRateVsHeroStatistics,
    stats.ItemUsageStatistics,
    stats.ItemBinaryUsageStatistics,
    stats.ItemWinRateStatistics,
    stats.ItemBinaryWinRateStatistics,
    stats.GameWinRateStatistics,
    stats.TrophyWinRateStatistics,
]


def display_menu():
    print("\nChoose an option:")
    print("0. Exit")
    for index, stat in enumerate(available_stats, 1):
        print(f"{index}. {stat.description}")


def main():
    user = input("Enter username: ").strip()
    filename = f"data/{user}_stats.json"

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print("Invalid user.")
        return

    while True:
        display_menu()
        choice = input("Enter choice: ").strip()

        try:
            choice = int(choice)
        except ValueError:
            print("Invalid input, please enter a number.")
            continue

        if choice == 0:
            break
        elif 1 <= choice <= len(available_stats):
            available_stats[choice - 1].display(data)
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
