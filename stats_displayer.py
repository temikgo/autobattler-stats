import json
import os

import stats

available_stats = [stats.RatingProgress]


def display_menu():
    print("\nChoose an option:")
    for index, stat in enumerate(available_stats, 1):
        print(f"{index}. {stat.description}")
    print(f"{len(available_stats) + 1}. Exit")


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
            if 1 <= choice <= len(available_stats):
                available_stats[choice - 1].display(data)
            elif choice == len(available_stats) + 1:
                break
            else:
                print("Invalid choice, please try again.")
        except ValueError:
            print("Invalid input, please enter a number.")


if __name__ == "__main__":
    main()
