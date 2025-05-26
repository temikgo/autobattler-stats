import json
import os

from autocomplete import input_with_autocomplete
from collections import Counter
from constants import HEROES, ITEMS, RELICS


def add_game():
    game = {}

    while True:
        result = input("  Win or Loss? (W/L): ").strip().upper()
        if result in ("W", "L"):
            game["result"] = result
            break
        print("  Invalid input. Please enter W or L.")

    while True:
        try:
            opponent_rating = int(input("  Opponent rating: "))
            break
        except ValueError:
            print("  Invalid input, please enter a number.")
    game["opponent_rating"] = opponent_rating

    game["opponent_hero"] = input_with_autocomplete(
        "  Opponent hero: ",
        "  Invalid hero. Please enter a valid hero name",
        options=HEROES,
        validator=lambda x: x.lower() in HEROES
    ).lower()

    items = {}
    item_count = 1
    print("  Enter your items one by one (press Enter on empty input to finish):")
    while True:
        item = input_with_autocomplete(
            f"    Item {item_count}: ",
            "    Invalid item. Please enter a valid item name.",
            options=ITEMS,
            validator=lambda x: not x or x.lower() in ITEMS
        )
        if not item:
            break
        item = item.lower()
        if item not in items:
            items[item] = 0
        items[item] += 1
        item_count += 1
    game["items"] = dict(sorted(items.items()))

    return game


def add_match():
    match = {}

    while True:
        try:
            start_rating = int(input("  Start rating: "))
            break
        except ValueError:
            print("Invalid input, please enter a number.")
    match["start_rating"] = start_rating

    while True:
        try:
            end_rating = int(input("  End rating: "))
            break
        except ValueError:
            print("Invalid input, please enter a number.")
    match["end_rating"] = end_rating

    match["hero"] = input_with_autocomplete(
        "  Hero: ",
        "  Invalid hero. Please enter a valid hero name",
        options=HEROES,
        validator=lambda x: x.lower() in HEROES
    ).lower()

    match["games"] = []

    game_count = 1
    while True:
        print(f"\nEnter data for game {game_count}:")

        game = add_game()
        game_count += 1

        match["games"].append(game)

        cont = input("Add another game? (y/n): ").strip().lower()
        if cont != 'y':
            break

    return match


def main():
    dirname = "data"
    user = input("Enter username: ").strip()
    filename = f"{dirname}/{user}_stats.json"

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "matches": []
        }

    match_count = 1
    while True:
        print(f"\nEnter data for match {match_count}:")

        match = add_match()
        match_count += 1

        data["matches"].append(match)

        cont = input("Add another match? (y/n): ").strip().lower()
        if cont != 'y':
            break

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\nAll matches successfully saved to {filename}")


if __name__ == "__main__":
    main()
