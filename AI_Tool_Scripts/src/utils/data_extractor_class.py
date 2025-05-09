import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt, atan2, degrees

# Class used to extract data from a folder containing image files and JSON config files.
# Features:
# 1. Load configuration data from JSON files in the specified folder.
# 2. Extract and process data from the image files and JSON files and save it to a CSV file.
# 3. Identify the frames that are flashing based on the configuration data.
# 4. Provide methods to retrieve the width, height, framerate and flashing frames of the images.
# 5. Provide method to calculate parameters like speed, direction, distance, and trajectory for each object and save to .csv
# 6. Provide methods to handle data export and visualization/plotting import per individual larvae.
# 7. Provide methods to stop the data extraction process if needed.

class DataExtractor:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.stop_flag = False
        self.rows = []
        self._config_data = {}
        self._flashing_frames = []
        self._width = 1
        self._height = 1
        self._framerate = 1.0
        self.label_dir = os.path.join(self.output_path, "labels")

        self.plot_colors = {
            "speed": "blue",
            "direction": "green",
            "distance": "orange",
            "trajectory": "purple"
        }

    def read_json_file(self, file_path):
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r") as f:
            return json.load(f)

    def extract_and_build_config_rows(self):
        if self.stop_flag:
            return

        config = self.read_json_file(os.path.join(self.input_path, 'config.json'))
        cam_config = self.read_json_file(os.path.join(self.input_path, 'config_cam.json'))
        timings = self.read_json_file(os.path.join(self.input_path, 'timings.json'))

        self._config_data["Optogenetic_LEDs"] = config.get("Optogenetic_LEDs", {})
        self._config_data["Camera"] = cam_config

        self.rows.append(["Config files", ""])
        self.rows.append(["Experiment_name", timings.get("Experiment_name", "")])
        self.rows.append(["Camera", ""])
        mode_value = cam_config.get("mode", "")
        self.rows.append(["Mode", mode_value])

        try:
            self._width = int(mode_value[0:4])
            self._height = int(mode_value[5:9])
        except Exception:
            self._width, self._height = 1, 1

        self.rows.append(["Capture Length", cam_config.get("capture_length", "")])
        self._framerate = float(cam_config.get("framerate", 1.0))
        self.rows.append(["Framerate", self._framerate])
        self.rows.append(["Gain", cam_config.get("gain", "")])
        self.rows.append(["Shutter Speed", cam_config.get("shutter_speed", "")])
        self.rows.append(["Capture time", timings.get("Camera", {}).get("capture_time", "")])

        ir = config.get("IR_LEDs", {})
        self.rows.append(["IR LEDs", ""])
        self.rows.append(["Duty Cycle", ir.get("duty_cycle", "")])
        self.rows.append(["Frequency", ir.get("frequency", "")])
        self.rows.append(["Active Time", ir.get("active_time", "")])

        opto = config.get("Optogenetic_LEDs", {})
        self.rows.append(["Optogenetic LEDs", ""])
        self.rows.append(["Duty Cycle", opto.get("duty_cycle", "")])
        self.rows.append(["Frequency", opto.get("frequency", "")])
        self.rows.append(["Flash Length", opto.get("flash_length", "")])
        self.rows.append(["Initial Delay", opto.get("initial_delay", "")])

        self.extract_flashing_frames()
        self.rows.append(["Flashing Frames"] + self._flashing_frames)

    def extract_flashing_frames(self):
        delay = 0.0
        length = 0.0
        fps = self._framerate

        for row in self.rows:
            if row[0] == "Initial Delay":
                delay = float(row[1] or 0.0)
            elif row[0] == "Flash Length":
                length = float(row[1] or 0.0)

        start_frame = int(delay * fps)
        end_frame = start_frame + int(length * fps) - 1 if length > 0 else start_frame
        self._flashing_frames = [f"{i:05d}" for i in range(start_frame, end_frame + 1)]

    def basic_parameters(self, df):
        df["Midpoint x centre"] = df["x centre"]
        df["Midpoint y centre"] = df["y centre"]
        df["Speed"] = 0.0
        df["Direction"] = 0.0
        df["Distance"] = 0.0
        df["Position x"] = df["x centre"] * self._width
        df["Position y"] = df["y centre"] * self._height

        grouped = df.groupby("object ID", group_keys=False)
        all_groups = []

        for _, group in grouped:
            group = group.sort_values("Frame").copy()
            speeds, directions, distances = [0], [0], [0]
            total_dist = 0

            for i in range(1, len(group)):
                dx = group.iloc[i]["x centre"] - group.iloc[i - 1]["x centre"]
                dy = group.iloc[i]["y centre"] - group.iloc[i - 1]["y centre"]
                dist = sqrt(dx**2 + dy**2)
                angle = degrees(atan2(dy, dx))

                speeds.append(dist * self._framerate)
                directions.append(angle)
                total_dist += dist
                distances.append(total_dist)

            group["Speed"] = speeds
            group["Direction"] = directions
            group["Distance"] = distances
            all_groups.append(group)

        return pd.concat(all_groups).sort_values(["object ID", "Frame"])

    def final_data_to_csv(self):
        self.extract_and_build_config_rows()
        data = []

        if os.path.exists(self.label_dir):
            for filename in sorted(os.listdir(self.label_dir)):
                if filename.endswith(".txt"):
                    frame_str = filename[-9:-4]
                    flashing_flag = "1" if frame_str in self._flashing_frames else "0"
                    file_path = os.path.join(self.label_dir, filename)

                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 6:
                                try:
                                    data.append([
                                        int(float(parts[0])),
                                        float(parts[1]), float(parts[2]),
                                        float(parts[3]), float(parts[4]),
                                        int(float(parts[5])),
                                        frame_str,
                                        flashing_flag
                                    ])
                                except ValueError:
                                    continue

        if data:
            columns = ["Class ID", "x centre", "y centre", "width", "height", "object ID", "Frame", "Flashing"]
            df = pd.DataFrame(data, columns=columns)
            df = self.basic_parameters(df)
            self.rows.append(["Larvae Data", ""])
            self.rows.append(list(df.columns))
            for row in df.itertuples(index=False):
                self.rows.append(list(row))

        output_file = os.path.join(self.output_path, "main_data.csv")
        pd.DataFrame(self.rows).to_csv(output_file, index=False, header=False)

    def larvae_data_exporter(self, main_csv_path, larvae_folder_path):
        if not os.path.exists(main_csv_path):
            print(f"{main_csv_path} not found.")
            return

        try:
            with open(main_csv_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            start_idx = None
            for i, line in enumerate(lines):
                if line.strip().startswith("Larvae Data"):
                    start_idx = i
                    break

            if start_idx is None or start_idx + 1 >= len(lines):
                print("Larvae Data section not found or invalid.")
                return

            df = pd.read_csv(main_csv_path, skiprows=start_idx + 1)
            df.dropna(axis=1, how='all', inplace=True)

            df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "")

            if "object ID" not in df.columns:
                print("No object ID column in CSV.")
                return

        except Exception as e:
            print(f"Failed to read {main_csv_path}: {e}")
            return

        for object_id in df["object ID"].unique():
            df_obj = df[df["object ID"] == object_id].copy()
            out_folder = os.path.join(larvae_folder_path, f"larvae_{object_id}")
            os.makedirs(out_folder, exist_ok=True)
            out_csv = os.path.join(out_folder, f"{object_id}_main_data.csv")
            df_obj.to_csv(out_csv, index=False)
            print(f"Saved: {out_csv}")

    def larvae_data_plotter(self, larvae_csv_path, output_folder_path):
        if not os.path.exists(larvae_csv_path):
            print(f"{larvae_csv_path} not found.")
            return

        try:
            df = pd.read_csv(larvae_csv_path)
            df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "")
        except Exception as e:
            print(f"Failed to read {larvae_csv_path}: {e}")
            return

        required_cols = {"Distance", "Speed", "Direction", "Midpoint x centre", "Midpoint y centre", "Frame"}
        if not required_cols.issubset(df.columns):
            print(f"Missing required data columns for plotting in {larvae_csv_path}")
            return

        object_id = os.path.basename(larvae_csv_path).split("_")[0]
        framerate = self.get_framerate()

        df["Time (s)"] = df["Frame"].astype(float) / framerate

        fig, axs = plt.subplots(1, 4, figsize=(22, 5))

        axs[0].plot(df["Time (s)"], df["Speed"], color=self.plot_colors["speed"])
        axs[0].set_title(f"Object {object_id} – Speed vs Time")
        axs[0].set_xlabel("Time (s)")
        axs[0].set_ylabel("Speed (pixels/sec)")

        axs[1].plot(df["Time (s)"], df["Direction"], color=self.plot_colors["direction"])
        axs[1].set_title(f"Object {object_id} – Direction vs Time")
        axs[1].set_xlabel("Time (s)")
        axs[1].set_ylabel("Direction (degrees)")

        axs[2].plot(df["Time (s)"], df["Distance"], color=self.plot_colors["distance"])
        axs[2].set_title(f"Object {object_id} – Accumulated Distance vs Time")
        axs[2].set_xlabel("Time (s)")
        axs[2].set_ylabel("Distance (pixels)")

        axs[3].plot(df["Midpoint x centre"], df["Midpoint y centre"], color=self.plot_colors["trajectory"])
        axs[3].set_title(f"Object {object_id} – Midpoint Trajectory")
        axs[3].set_xlabel("x position (normalized)")
        axs[3].set_ylabel("y position (normalized)")

        plt.tight_layout()
        plot_path = os.path.join(output_folder_path, f"{object_id}_larvae_data_plot.png")
        plt.savefig(plot_path)
        plt.close()
        print(f"Plot saved to: {plot_path}")

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_flashing_frames(self):
        return self._flashing_frames
    
    def get_framerate(self):
        return self._framerate
    
