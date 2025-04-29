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
    def display(data):
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
        cursor.connect("add", lambda sel: sel.annotation.set_text(f"Rating: {y_values[int(sel.index)]}"))

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
        k = kwargs.get("k", 10)
        top_items, win_counts, loss_counts = ItemUsageStatistics.calculate_usage(data, k)

        x_values = range(len(top_items))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        bars_wins = plt.bar(x_values, win_counts, label="Wins", color='green', edgecolor='black')
        bars_lossess = plt.bar(x_values, loss_counts, bottom=win_counts, label="Losses", color='red', edgecolor='black')

        plt.xticks(x_values, top_items, rotation=45, ha="right")
        plt.ylabel("Total Usage")
        plt.title(f"Top {k} Item Usage (Wins vs Losses)")
        plt.legend()
        plt.tight_layout()

        cursor = mplcursors.cursor(bars_wins, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"Win Percentage: {win_counts[sel.index] / (win_counts[sel.index] + loss_counts[sel.index]) * 100:.2f}%"
        ))

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
        k = kwargs.get("k", 10)
        top_items, win_counts, loss_counts = ItemBinaryUsageStatistics.calculate_usage(data, k)

        x_values = range(len(top_items))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        bars_wins = plt.bar(x_values, win_counts, label="Wins", color='green', edgecolor='black')
        bars_lossess = plt.bar(x_values, loss_counts, bottom=win_counts, label="Losses", color='red', edgecolor='black')

        plt.xticks(x_values, top_items, rotation=45, ha="right")
        plt.ylabel("Total Usage (binary per game)")
        plt.title(f"Top {k} Item Usage (Wins vs Losses)")
        plt.legend()
        plt.tight_layout()

        cursor = mplcursors.cursor(bars_wins, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"Win Rate: {win_counts[sel.index] / (win_counts[sel.index] + loss_counts[sel.index]) * 100:.2f}%"
        ))

        plt.show()


class ItemWinRateStatistics(StatisticsFunction):
    description = "Show top items by win rate"

    @staticmethod
    def calculate_win_rates(data, k, min_games):
        win_counts = {}
        game_counts = {}

        for match in data["matches"]:
            for game in match["games"]:
                result = game["result"]
                for item in game["items"]:
                    if item not in win_counts:
                        win_counts[item] = 0
                        game_counts[item] = 0
                    game_counts[item] += 1
                    if result == "W":
                        win_counts[item] += 1

        win_rates = [(item, win_counts[item] / game_counts[item]) 
                     for item in win_counts if game_counts[item] >= min_games]
        sorted_win_rates = sorted(win_rates, key=lambda x: x[1], reverse=True)
        top_items, top_win_rates = zip(*sorted_win_rates[:k])

        return top_items, top_win_rates

    @staticmethod
    def display(data, **kwargs):
        k = kwargs.get("k", 10)
        min_games = kwargs.get("min_games", 20)
        top_items, win_rates = ItemWinRateStatistics.calculate_win_rates(data, k, min_games)

        win_rates = [win_rate * 100 for win_rate in win_rates]
        x_values = range(len(top_items))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        cmap = cm.get_cmap('RdYlGn')
        norm = plt.Normalize(vmin=0, vmax=100)

        bars = plt.bar(x_values, win_rates, color=cmap(norm(win_rates)), edgecolor='black')

        plt.xticks(x_values, top_items, rotation=45, ha="right")
        plt.ylabel("Win Rate")
        plt.title(f"Top {k} Items by Win Rate")
        plt.ylim(0, 100)
        plt.tight_layout()

        cursor = mplcursors.cursor(bars, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"Win Rate: {win_rates[sel.index]:.2f}%"
        ))

        plt.show()
