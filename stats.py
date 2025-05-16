from collections import Counter
from matplotlib import patheffects
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import mplcursors
import numpy as np

from constants import RANKS, RELICS, UNIQUES


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
        min_rating, max_rating = min(y_values), max(y_values)

        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(10, 6))

        padding = (max_rating - min_rating) * 0.05
        visible_min = min_rating - padding
        visible_max = max_rating + padding
        visible_zones = [
            zone for zone in RANKS 
            if zone[0] <= max_rating and zone[1] >= min_rating
        ]

        for start, end, color, label in visible_zones:
            draw_start = max(start, visible_min)
            draw_end = min(end, visible_max)
            ax.axhspan(draw_start, draw_end, facecolor=color, alpha=0.7)
            if start >= min_rating or end <= max_rating:
                label_pos = (max(start, min_rating) + min(end, max_rating)) / 2
                ax.text(1.02, label_pos, f"{label} ({start}-{end})", 
                    transform=ax.get_yaxis_transform(),
                    va='center', ha='left', color='dimgray')

        ax.plot(x_values, y_values, linestyle='-', color='black', linewidth=2)
        points = ax.scatter(x_values, y_values, color='black', zorder=3)

        ax.set_ylim(min_rating - padding, max_rating + padding)
        
        ax.set_xlabel("Match Number")
        ax.set_ylabel("Rating")
        ax.set_title("Rating Progress")
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


class AccurateWinRateByRating(StatisticsFunction):
    description = "Accurate win rate estimation by opponent rating"

    @staticmethod
    def prepare_data(data):
        ratings = []
        results = []
        for match in data["matches"]:
            for game in match["games"]:
                rating = game.get("opponent_rating")
                if rating is None or not np.isfinite(rating):
                    continue
                ratings.append(float(rating))
                results.append(1 if game.get("result") == "W" else 0)

        return np.array(ratings), np.array(results)

    @staticmethod
    def display(data, **kwargs):
        ratings, results = AccurateWinRateByRating.prepare_data(data)

        plt.figure(figsize=(14, 7))
        plt.style.use('seaborn-v0_8-darkgrid')

        x_values = np.linspace(min(ratings), max(ratings), 100)

        winrates = []
        for x in x_values:
            weights = np.exp(-0.5*((ratings - x)/(0.15*(max(ratings)-min(ratings))))**2)
            winrates.append(np.average(results, weights=weights))
        winrates = np.array(winrates)

        plt.plot(x_values, winrates, color='#3a86ff', linewidth=3, label='Win probability')

        plt.axhline(0.5, color='black', linestyle=':', alpha=0.5)
        plt.title(f"Win Rate vs Opponent Rating", fontsize=16, pad=20)
        plt.xlabel("Opponent Rating", fontsize=12)
        plt.ylabel("Win Probability", fontsize=12)
        plt.ylim(0, 1)
        plt.legend()
        plt.grid(True, alpha=0.3)

        ax2 = plt.gca().twinx()
        ax2.hist(ratings, bins=20, color='gray', alpha=0.2)
        ax2.set_ylabel('Game count', fontsize=12)

        plt.tight_layout()
        plt.show()


class OpponentHeroDistribution(StatisticsFunction):
    description = "Show distribution of opponent heroes"

    @staticmethod
    def calculate_games(data, min_games):
        game_counts = {}

        for match in data["matches"]:
            for game in match["games"]:
                opponent = game["opponent_hero"]
                if opponent not in game_counts:
                    game_counts[opponent] = 0
                game_counts[opponent] += 1

        filtered_counts = {hero: count for hero, count in game_counts.items() if count >= min_games}
        sorted_counts = sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)
        heroes, games = zip(*sorted_counts)

        return heroes, games


    @staticmethod
    def display(data, **kwargs):
        min_games = kwargs.get("min_games", 5)
        heroes, games = OpponentHeroDistribution.calculate_games(data, min_games)

        plt.style.use('seaborn-v0_8-dark')
        plt.rcParams['font.family'] = 'DejaVu Sans'

        fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
        fig.patch.set_facecolor('#2e2e2e')
        ax.set_facecolor('#2e2e2e')

        colors = plt.cm.viridis(np.linspace(0, 1, len(heroes)))

        wedges, texts, autotexts = ax.pie(
            games,
            labels=None,
            autopct='%1.2f%%',
            startangle=90,
            colors=colors,
            wedgeprops={
                'edgecolor': 'white',
                'linewidth': 0.5,
                'width': 0.6
            },
            pctdistance=0.85,
            textprops={
                'fontsize': 10,
                'fontweight': 'bold',
                'color': 'white',
                'path_effects': [
                    patheffects.withStroke(linewidth=2, foreground='black')
                ]
            },
            rotatelabels=True
        )

        centre_circle = plt.Circle((0,0), 0.4, color='#2e2e2e', fc='#2e2e2e', linewidth=0)
        fig.gca().add_artist(centre_circle)

        legend = ax.legend(
            wedges,
            [f"{h} ({g})" for h, g in zip(heroes, games)],
            title="Heroes (Games)",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize=10,
            title_fontsize=12,
            framealpha=0.9,
            labelcolor='white',
            facecolor='#3e3e3e',
            edgecolor='white'
        )
        legend.get_title().set_color('white')

        total_games = sum(games)
        ax.set_title(
            f"Opponent Hero Distribution\nTotal Games: {total_games} | Min Games: {min_games}",
            fontsize=14,
            fontweight='bold',
            color='white',
            pad=20
        )

        plt.tight_layout()
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


class RelicWinRateStatistics(StatisticsFunction):
    description = "Show win rate for each relic"

    @staticmethod
    def calculate_win_rates(data, min_games):
        game_counts = {}
        win_counts = {}

        for match in data["matches"]:
            for game in match["games"]:
                result = game["result"]
                for item in game["items"]:
                    if item in RELICS:
                        if item not in game_counts:
                            win_counts[item] = 0
                            game_counts[item] = 0
                        game_counts[item] += 1
                        if result == "W":
                            win_counts[item] += 1

        win_rates = [(item, win_counts[item] / game_counts[item]) 
                     for item in win_counts if game_counts[item] >= min_games]
        sorted_win_rates = sorted(win_rates, key=lambda x: x[1], reverse=True)
        relics, win_rates = zip(*sorted_win_rates)

        return relics, win_rates

    @staticmethod
    def display(data, **kwargs):
        min_games = kwargs.get("min_games", 20)
        relics, win_rates = RelicWinRateStatistics.calculate_win_rates(data, min_games)

        win_rates = [win_rate * 100 for win_rate in win_rates]
        x_values = range(len(relics))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        cmap = cm.get_cmap('RdYlGn')
        norm = plt.Normalize(vmin=0, vmax=100)

        bars = plt.bar(x_values, win_rates, color=cmap(norm(win_rates)), edgecolor='black')

        plt.xticks(x_values, relics, rotation=45, ha="right")
        plt.ylabel("Win Rate")
        plt.title(f"Relics Win Rate")
        plt.ylim(0, 100)
        plt.tight_layout()

        cursor = mplcursors.cursor(bars, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            sel.annotation.set_text(f"{relics[sel.index]}: {win_rates[sel.index]:.2f}%")
            sel.annotation.get_bbox_patch().update({
                "facecolor": "white",
                "edgecolor": "black",
                "boxstyle": "round,pad=0.5",
                "alpha": 0.9,
                "linewidth": 1.2
            })
            sel.annotation.set_fontsize(10)

        plt.show()


class UniqueWinRateStatistics(StatisticsFunction):
    description = "Show win rate for each unique item"

    @staticmethod
    def calculate_win_rates(data, min_games):
        game_counts = {}
        win_counts = {}

        for match in data["matches"]:
            for game in match["games"]:
                result = game["result"]
                for item in game["items"]:
                    if item in UNIQUES[match["hero"]]:
                        if item not in game_counts:
                            win_counts[item] = 0
                            game_counts[item] = 0
                        game_counts[item] += 1
                        if result == "W":
                            win_counts[item] += 1

        win_rates = [(item, win_counts[item] / game_counts[item]) 
                     for item in win_counts if game_counts[item] >= min_games]
        sorted_win_rates = sorted(win_rates, key=lambda x: x[1], reverse=True)
        relics, win_rates = zip(*sorted_win_rates)

        return relics, win_rates

    @staticmethod
    def display(data, **kwargs):
        min_games = kwargs.get("min_games", 20)
        relics, win_rates = UniqueWinRateStatistics.calculate_win_rates(data, min_games)

        win_rates = [win_rate * 100 for win_rate in win_rates]
        x_values = range(len(relics))

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(12, 6))

        cmap = cm.get_cmap('RdYlGn')
        norm = plt.Normalize(vmin=0, vmax=100)

        bars = plt.bar(x_values, win_rates, color=cmap(norm(win_rates)), edgecolor='black')

        plt.xticks(x_values, relics, rotation=45, ha="right")
        plt.ylabel("Win Rate")
        plt.title(f"Uniques Win Rate")
        plt.ylim(0, 100)
        plt.tight_layout()

        cursor = mplcursors.cursor(bars, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            sel.annotation.set_text(f"{relics[sel.index]}: {win_rates[sel.index]:.2f}%")
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


class SmartItemWinRateStatistics(StatisticsFunction):
    description = "Show top items by advanced effectiveness metrics"

    @staticmethod
    def calculate_metrics(data, k=30, min_games=20):
        total_games = sum(len(match["games"]) for match in data["matches"])
        total_wins = sum(1 for match in data["matches"] for game in match["games"] if game["result"] == "W")
        overall_win_rate = total_wins / total_games

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

        metrics = {}
        for item in game_counts:
            if game_counts[item] < min_games:
                continue

            wins = win_counts[item]
            games = game_counts[item]
            wr = wins / games

            bayesian_wr = (wins + overall_win_rate * 10) / (games + 10)

            z = 1.96
            p_hat = wr
            n = games
            wilson_lower = (p_hat + z*z/(2*n) - z*((p_hat*(1-p_hat)+z*z/(4*n))/n)**0.5)/(1+z*z/n)

            lift = (wr - overall_win_rate) / overall_win_rate * 100

            eb_shrinkage = 1 - (10 / (games + 10))
            eb_wr = overall_win_rate * (1 - eb_shrinkage) + wr * eb_shrinkage
            
            metrics[item] = {
                'games': games,
                'win_rate': wr,
                'bayesian': bayesian_wr,
                'wilson_lower': wilson_lower,
                'lift': lift,
                'empirical_bayes': eb_wr,
                'combined_score': (bayesian_wr * 0.4 + wilson_lower * 0.3 + eb_wr * 0.3) * 100
            }

        return metrics, overall_win_rate

    @staticmethod
    def display(data, metric='combined_score', **kwargs):
        k = kwargs.get("k", 30)
        min_games = kwargs.get("min_games", 20)
        
        metrics, overall_win_rate = SmartItemWinRateStatistics.calculate_metrics(data, k, min_games)

        sorted_items = sorted(metrics.items(), key=lambda x: x[1][metric], reverse=True)[:k]
        
        items = [item[0] for item in sorted_items]
        values = [item[1][metric] for item in sorted_items]
        games = [item[1]['games'] for item in sorted_items]
        raw_wr = [item[1]['win_rate']*100 for item in sorted_items]

        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(14, 7))

        norm = plt.Normalize(min(values)*0.9, max(values)*1.1)
        cmap = cm.get_cmap('RdYlGn')

        bars = ax.bar(items, values, color=cmap(norm(values)), edgecolor='black')

        ax.scatter(items, raw_wr, color='blue', alpha=0.5, label='Raw Win Rate')
        ax.axhline(overall_win_rate*100, color='red', linestyle='--', label=f'Overall WR ({overall_win_rate*100:.2f}%)')

        ax.set_ylabel("Score" if metric != 'lift' else "Lift (%)")
        ax.set_title(f"Top {k} Items by {metric.replace('_', ' ').title()}")
        ax.legend()
        plt.xticks(range(len(items)), items, rotation=45, ha="right")
        plt.tight_layout()

        cursor = mplcursors.cursor(bars, hover=True)
        cursor._epsilon = 3

        @cursor.connect("add")
        def on_hover(sel):
            item = items[sel.index]
            info = metrics[item]
            text = (f"{item}\n"
                   f"Games: {info['games']}\n"
                   f"Raw WR: {info['win_rate']*100:.2f}%\n"
                   f"Bayesian: {info['bayesian']*100:.2f}%\n"
                   f"Wilson Lower: {info['wilson_lower']*100:.2f}%\n"
                   f"Emp. Bayes: {info['empirical_bayes']*100:.2f}%\n"
                   f"Lift: {info['lift']:.2f}%\n"
                   f"Combined score: {info['combined_score']:.2f}%")

            sel.annotation.set_text(text)
            sel.annotation.get_bbox_patch().update({
                "facecolor": "white",
                "edgecolor": "black",
                "boxstyle": "round,pad=0.5",
                "alpha": 0.9,
                "linewidth": 1.2
            })
            sel.annotation.set_fontsize(10)

        plt.show()
