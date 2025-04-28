import json
import matplotlib.pyplot as plt

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

        plt.figure(figsize=(10, 6))
        plt.plot(x_values, y_values, marker='o', linestyle='-', color='b')

        plt.xlabel("Match Number")
        plt.ylabel("Rating")
        plt.title("Rating Progress with Gaps")
        plt.xticks([range(1, len(data["matches"]) + 1), [str(i) for i in range(1, len(data["matches"]) + 1)]])

        plt.tight_layout()

        plt.show()
