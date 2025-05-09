import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

# Class to analyze head-tail distance from a CSV file
# Workflow:
# 1. Load the CSV file containing head and tail coordinates.
# 2. Compute the Euclidean distance between the head and tail.
# 3. Plot the distance over time and save the plot as a PNG file.
# 4. Handle exceptions and provide informative error messages.

# Note: 
# Not part of GUI yet, but can be used as a standalone script.
# Can pass tuple of (csv_path, output_folder) allowing for multiple files to be processed in a single run.

class HeadTailDistanceAnalyzer:
    def __init__(self, csv_path, output_folder, fps=10):
        self.csv_path = csv_path
        self.output_folder = output_folder
        self.fps = fps
        self.df = None
        self.distances = None
        self.time = None

    def load_csv(self):
        try:
            self.df = pd.read_csv(self.csv_path, header=[0, 1, 2])
            print(f"Loaded CSV: {self.csv_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load CSV: {e}")

    def compute_distances(self):
        try:
            head_x = self.df[('Adjust_for_header_for_your_csv', 'Head', 'x')]
            head_y = self.df[('Adjust_for_header_for_your_csv', 'Head', 'y')]
            tail_x = self.df[('Adjust_for_header_for_your_csv', 'Tail', 'x')]
            tail_y = self.df[('Adjust_for_header_for_your_csv', 'Tail', 'y')]

            self.distances = np.sqrt((head_x - tail_x) ** 2 + (head_y - tail_y) ** 2)
            self.time = np.arange(len(self.distances)) / self.fps
        except Exception as e:
            raise RuntimeError(f"Failed to compute distances: {e}")

    def plot_distance_over_time(self):
        os.makedirs(self.output_folder, exist_ok=True)

        filename = os.path.basename(self.csv_path).replace(".csv", "_distance_plot.png")
        out_path = os.path.join(self.output_folder, filename)

        plt.figure(figsize=(10, 5))
        plt.plot(self.time, self.distances, label="Head-Tail Distance", color="blue")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Distance (pixels)")
        plt.title(f"Head-Tail Distance Over Time\n{os.path.basename(self.csv_path)}")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close()
        print(f"Plot saved to: {out_path}")

    def run(self):
        self.load_csv()
        self.compute_distances()
        self.plot_distance_over_time()

if __name__ == "__main__":
    paths = [
        ("./dir/to/.csv", "./dir/to/output_folder"),
    ]

    for csv_path, out_dir in paths:
        try:
            analyzer = HeadTailDistanceAnalyzer(csv_path, out_dir)
            analyzer.run()
        except Exception as e:
            print(f"Failed on: {csv_path}\n{e}")
