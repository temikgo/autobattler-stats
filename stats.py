from collections import Counter
import json
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import mplcursors

class StatisticsFunction:
    description = ""
    
    @staticmethod
    def display(data):
        raise NotImplementedError("Subclasses should implement this method.")



class RatingProgress(StatisticsFunction):
    description = "Show rating progress"

    @staticmethod
    def calculate_ratings(data):
        x_values, y_values = [], []

        if data["matches"]: 
            x_values.append(0)
            y_values.append(data["matches"][0]["start_rating"])
            x_values.append(1)
            y_values.append(data["matches"][0]["end_rating"])

            x = 2
            for i in range(1, len(data["matches"])):
                if data["matches"][i - 1]["end_rating"] != data["matches"][i]["start_rating"]:
                    x_values.append(x - 0.5)
                    y_values.append(None)
                    x_values.append(x)
                    y_values.append(data["matches"][i]["start_rating"])
                    x += 1
                x_values.append(x)
                y_values.append(data["matches"][i]["end_rating"])
                x += 1

        return x_values, y_values

    @staticmethod
    def display(data, **kwargs):
        x_values, y_values = RatingProgress.calculate_ratings(data)

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(10, 6))

        plt.plot(x_values, y_values, linestyle='-', color='b')
        points = plt.scatter(x_values, y_values, color='b')

        plt.xlabel("Match Number")
        plt.ylabel("Rating")
        plt.title("Rating Progress")
        plt.tight_layout()

        cursor = mplcursors.cursor(points, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            sel.annotation.set_text(f"Rating: {y_values[int(sel.index)]}")
            sel.annotation.get_bbox_patch().update({
                "facecolor": "white",
                "edgecolor": "black",
                "boxstyle": "round,pad=0.5",
                "alpha": 0.9,
                "linewidth": 1.2
            })
            sel.annotation.set_fontsize(10)

        plt.show()


class WinRateVsHeroStatistics(StatisticsFunction):
    description = "Show win rate against each opponent hero"

    @staticmethod
    def calculate_win_rates(data, min_games):
        win_counts = {}
        game_counts = {}

        for match in data["matches"]:
            for game in match["games"]:
                opponent = game["opponent_hero"]
                if opponent not in game_counts:
                    game_counts[opponent] = 0
                    win_counts[opponent] = 0
                game_counts[opponent] += 1
                if game["result"] == "W":
                    win_counts[opponent] += 1

        win_rates = [(hero, win_counts[hero] / game_counts[hero])
                     for hero in game_counts if game_counts[hero] >= min_games]
        sorted_win_rates = sorted(win_rates, key=lambda x: x[1], reverse=True)
        opponent_heroes, win_rates = zip(*sorted_win_rates)

        return opponent_heroes, win_rates

    @staticmethod
    def display(data, **kwargs):
        min_games = kwargs.get("min_games", 5)
        opponent_heroes, win_rates = WinRateVsHeroStatistics.calculate_win_rates(data, min_games)

        win_rates = [win_rate * 100 for win_rate in win_rates]
        x_values = range(len(opponent_heroes))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        cmap = cm.get_cmap('RdYlGn')
        norm = plt.Normalize(vmin=0, vmax=100)

        bars = plt.bar(x_values, win_rates, color=cmap(norm(win_rates)), edgecolor='black')

        plt.xticks(x_values, opponent_heroes, rotation=45, ha="right")
        plt.ylabel("Win Rate")
        plt.title(f"Win Rate vs Opponent Heroes")
        plt.ylim(0, 100)
        plt.tight_layout()

        cursor = mplcursors.cursor(bars, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            sel.annotation.set_text(f"{opponent_heroes[sel.index]}: {win_rates[sel.index]:.2f}%")
            sel.annotation.get_bbox_patch().update({
                "facecolor": "white",
                "edgecolor": "black",
                "boxstyle": "round,pad=0.5",
                "alpha": 0.9,
                "linewidth": 1.2
            })
            sel.annotation.set_fontsize(10)

        plt.show()


class ItemUsageStatistics(StatisticsFunction):
    description = "Show item usage statistics"

    @staticmethod
    def calculate_usage(data, k):
        total_usage = Counter()
        win_usage = Counter()
        loss_usage = Counter()

        for match in data["matches"]:
            for game in match["games"]:
                result = game["result"]
                for item, count in game["items"].items():
                    total_usage[item] += count
                    if result == "W":
                        win_usage[item] += count
                    else:
                        loss_usage[item] += count

        top_items = [item for item, _ in total_usage.most_common(k)]
        win_counts = [win_usage[item] for item in top_items]
        loss_counts = [loss_usage[item] for item in top_items]

        return top_items, win_counts, loss_counts

    @staticmethod
    def display(data, **kwargs):
        k = kwargs.get("k", 30)
        top_items, win_counts, loss_counts = ItemUsageStatistics.calculate_usage(data, k)

        x_values = range(len(top_items))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        bars_wins = plt.bar(x_values, win_counts, label="Wins", color='green', edgecolor='black')
        bars_losses = plt.bar(x_values, loss_counts, bottom=win_counts, label="Losses", color='red', edgecolor='black')

        plt.xticks(x_values, top_items, rotation=45, ha="right")
        plt.ylabel("Total Usage")
        plt.title(f"Top {k} Item Usage (Wins vs Losses)")
        plt.legend()
        plt.tight_layout()

        cursor = mplcursors.cursor(bars_wins + bars_losses, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            bar = sel.artist
            sel.annotation.get_bbox_patch().update({
                "facecolor": "white",
                "edgecolor": "black",
                "boxstyle": "round,pad=0.5",
                "alpha": 1.0,
                "linewidth": 1.2
            })
            sel.annotation.set_fontsize(10)
            for index, b in enumerate(bars_wins):
                if b == bar:
                    win_pct = win_counts[index] / (win_counts[index] + loss_counts[index]) * 100
                    sel.annotation.set_text(
                        f"{top_items[index]}\nWin Rate: {win_pct:.2f}%"
                    )
                    return
            for index, b in enumerate(bars_losses):
                if b == bar:
                    total = win_counts[index] + loss_counts[index]
                    sel.annotation.set_text(
                        f"{top_items[index]}\nTotal games: {total}"
                    )
                    return

        plt.show()


class ItemBinaryUsageStatistics(StatisticsFunction):
    description = "Show item usage (binary per game) statistics"

    @staticmethod
    def calculate_usage(data, k):
        total_usage = Counter()
        win_usage = Counter()
        loss_usage = Counter()

        for match in data["matches"]:
            for game in match["games"]:
                result = game["result"]
                for item in game["items"]:
                    total_usage[item] += 1
                    if result == "W":
                        win_usage[item] += 1
                    else:
                        loss_usage[item] += 1

        top_items = [item for item, _ in total_usage.most_common(k)]
        win_counts = [win_usage[item] for item in top_items]
        loss_counts = [loss_usage[item] for item in top_items]

        return top_items, win_counts, loss_counts

    @staticmethod
    def display(data, **kwargs):
        k = kwargs.get("k", 30)
        top_items, win_counts, loss_counts = ItemBinaryUsageStatistics.calculate_usage(data, k)

        x_values = range(len(top_items))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        bars_wins = plt.bar(x_values, win_counts, label="Wins", color='green', edgecolor='black')
        bars_losses = plt.bar(x_values, loss_counts, bottom=win_counts, label="Losses", color='red', edgecolor='black')

        plt.xticks(x_values, top_items, rotation=45, ha="right")
        plt.ylabel("Total Usage (binary per game)")
        plt.title(f"Top {k} Item Usage (Wins vs Losses)")
        plt.legend()
        plt.tight_layout()

        cursor = mplcursors.cursor(bars_wins + bars_losses, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            bar = sel.artist
            sel.annotation.get_bbox_patch().update({
                "facecolor": "white",
                "edgecolor": "black",
                "boxstyle": "round,pad=0.5",
                "alpha": 1.0,
                "linewidth": 1.2
            })
            sel.annotation.set_fontsize(10)
            for index, b in enumerate(bars_wins):
                if b == bar:
                    win_pct = win_counts[index] / (win_counts[index] + loss_counts[index]) * 100
                    sel.annotation.set_text(
                        f"{top_items[index]}\nWin Rate: {win_pct:.2f}%"
                    )
                    return
            for index, b in enumerate(bars_losses):
                if b == bar:
                    total = win_counts[index] + loss_counts[index]
                    sel.annotation.set_text(
                        f"{top_items[index]}\nTotal games: {total}"
                    )
                    return

        plt.show()


class ItemWinRateStatistics(StatisticsFunction):
    description = "Show top items by win rate"

    @staticmethod
    def calculate_win_rates(data, k, min_games):
        game_counts = {}
        win_counts = {}

        for match in data["matches"]:
            for game in match["games"]:
                result = game["result"]
                for item, count in game["items"].items():
                    if item not in game_counts:
                        win_counts[item] = 0
                        game_counts[item] = 0
                    game_counts[item] += count
                    if result == "W":
                        win_counts[item] += count

        win_rates = [(item, win_counts[item] / game_counts[item]) 
                     for item in win_counts if game_counts[item] >= min_games]
        sorted_win_rates = sorted(win_rates, key=lambda x: x[1], reverse=True)
        items, win_rates = zip(*sorted_win_rates[:k])

        return items, win_rates

    @staticmethod
    def display(data, **kwargs):
        k = kwargs.get("k", 30)
        min_games = kwargs.get("min_games", 20)
        items, win_rates = ItemWinRateStatistics.calculate_win_rates(data, k, min_games)

        win_rates = [win_rate * 100 for win_rate in win_rates]
        x_values = range(len(items))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        cmap = cm.get_cmap('RdYlGn')
        norm = plt.Normalize(vmin=0, vmax=100)

        bars = plt.bar(x_values, win_rates, color=cmap(norm(win_rates)), edgecolor='black')

        plt.xticks(x_values, items, rotation=45, ha="right")
        plt.ylabel("Win Rate")
        plt.title(f"Top {k} Items by Win Rate")
        plt.ylim(0, 100)
        plt.tight_layout()

        cursor = mplcursors.cursor(bars, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            sel.annotation.set_text(f"{items[sel.index]}\nWin Rate: {win_rates[sel.index]:.2f}%")
            sel.annotation.get_bbox_patch().update({
                "facecolor": "white",
                "edgecolor": "black",
                "boxstyle": "round,pad=0.5",
                "alpha": 0.9,
                "linewidth": 1.2
            })
            sel.annotation.set_fontsize(10)

        plt.show()


class ItemBinaryWinRateStatistics(StatisticsFunction):
    description = "Show top items by win rate (binary per game)"

    @staticmethod
    def calculate_win_rates(data, k, min_games):
        game_counts = {}
        win_counts = {}

        for match in data["matches"]:
            for game in match["games"]:
                result = game["result"]
                for item in game["items"]:
                    if item not in game_counts:
                        game_counts[item] = 0
                        win_counts[item] = 0
                    game_counts[item] += 1
                    if result == "W":
                        win_counts[item] += 1

        win_rates = [(item, win_counts[item] / game_counts[item]) 
                     for item in win_counts if game_counts[item] >= min_games]
        sorted_win_rates = sorted(win_rates, key=lambda x: x[1], reverse=True)
        items, win_rates = zip(*sorted_win_rates[:k])

        return items, win_rates

    @staticmethod
    def display(data, **kwargs):
        k = kwargs.get("k", 30)
        min_games = kwargs.get("min_games", 20)
        items, win_rates = ItemBinaryWinRateStatistics.calculate_win_rates(data, k, min_games)

        win_rates = [win_rate * 100 for win_rate in win_rates]
        x_values = range(len(items))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        cmap = cm.get_cmap('RdYlGn')
        norm = plt.Normalize(vmin=0, vmax=100)

        bars = plt.bar(x_values, win_rates, color=cmap(norm(win_rates)), edgecolor='black')

        plt.xticks(x_values, items, rotation=45, ha="right")
        plt.ylabel("Win Rate (binary per game)")
        plt.title(f"Top {k} Items by Win Rate")
        plt.ylim(0, 100)
        plt.tight_layout()

        cursor = mplcursors.cursor(bars, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            sel.annotation.set_text(f"{items[sel.index]}\nWin Rate: {win_rates[sel.index]:.2f}%")
            sel.annotation.get_bbox_patch().update({
                "facecolor": "white",
                "edgecolor": "black",
                "boxstyle": "round,pad=0.5",
                "alpha": 0.9,
                "linewidth": 1.2
            })
            sel.annotation.set_fontsize(10)

        plt.show()


class GameWinRateStatistics(StatisticsFunction):
    description = "Show win rate by game number inside match"

    @staticmethod
    def calculate_win_rates(data, min_games=5):
        win_counts = {}
        game_counts = {}

        for match in data["matches"]:
            for i, game in enumerate(match["games"]):
                game_num = i + 1
                if game_num not in game_counts:
                    game_counts[game_num] = 0
                    win_counts[game_num] = 0
                game_counts[game_num] += 1
                if game["result"] == "W":
                    win_counts[game_num] += 1

        win_rates = [(game_num, win_counts[game_num] / game_counts[game_num])
                     for game_num in game_counts]
        sorted_win_rates = sorted(win_rates, key=lambda x: x[0])
        games, win_rates = zip(*sorted_win_rates)

        return games, win_rates

    @staticmethod
    def display(data, **kwargs):
        games, win_rates = GameWinRateStatistics.calculate_win_rates(data)

        win_rates = [win_rate * 100 for win_rate in win_rates]
        x_values = range(len(games))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        cmap = cm.get_cmap('RdYlGn')
        norm = plt.Normalize(vmin=0, vmax=100)
        colors = cmap(norm(win_rates))

        bars = plt.bar(x_values, win_rates, color=colors, edgecolor='black')

        plt.xticks(x_values, [str(i) for i in games])
        plt.ylabel("Win Rate (%)")
        plt.title("Win Rate by Game Number")
        plt.ylim(0, 100)
        plt.tight_layout()

        cursor = mplcursors.cursor(bars, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            sel.annotation.set_text(f"Game {games[sel.index]}: {win_rates[sel.index]:.2f}%")
            sel.annotation.get_bbox_patch().update({
                "facecolor": "white",
                "edgecolor": "black",
                "boxstyle": "round,pad=0.5",
                "alpha": 0.9,
                "linewidth": 1.2
            })
            sel.annotation.set_fontsize(10)

        plt.show()


class TrophyWinRateStatistics(StatisticsFunction):
    description = "Show win rate by trophy count in match"

    @staticmethod
    def calculate_win_rates(data):
        win_counts = {}
        trophy_counts = {}

        for match in data["matches"]:
            trophies = 0
            for game in match["games"]:
                if trophies not in trophy_counts:
                    trophy_counts[trophies] = 0
                    win_counts[trophies] = 0
                trophy_counts[trophies] += 1
                if game["result"] == "W":
                    win_counts[trophies] += 1
                    trophies += 1

        win_rates = [(trophies, win_counts[trophies] / trophy_counts[trophies])
                     for trophies in trophy_counts]
        sorted_win_rates = sorted(win_rates, key=lambda x: x[0])
        trophies, win_rates = zip(*sorted_win_rates)

        return trophies, win_rates

    @staticmethod
    def display(data, **kwargs):
        trophies, win_rates = TrophyWinRateStatistics.calculate_win_rates(data)

        win_rates = [win_rate * 100 for win_rate in win_rates]
        x_values = range(len(trophies))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        cmap = cm.get_cmap('RdYlGn')
        norm = plt.Normalize(vmin=0, vmax=100)
        colors = cmap(norm(win_rates))

        bars = plt.bar(x_values, win_rates, color=colors, edgecolor='black')

        plt.xticks(x_values, [str(i) for i in trophies])
        plt.ylabel("Win Rate (%)")
        plt.title("Win Rate by Trophy Count")
        plt.ylim(0, 100)
        plt.tight_layout()

        cursor = mplcursors.cursor(bars, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            sel.annotation.set_text(f"Trophies {trophies[sel.index]}: {win_rates[sel.index]:.2f}%")
            sel.annotation.get_bbox_patch().update({
                "facecolor": "white",
                "edgecolor": "black",
                "boxstyle": "round,pad=0.5",
                "alpha": 0.9,
                "linewidth": 1.2
            })
            sel.annotation.set_fontsize(10)

        plt.show()
