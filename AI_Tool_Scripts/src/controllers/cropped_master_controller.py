import os
import shutil
import traceback
import time
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox

from utils.remove_hidden_class import RemoveHiddenFiles
from utils.bit_depth_convert_class import BitDepthConverter
from utils.larvae_object_cropper import LarvaeObjectCropper
from utils.data_extractor_class import DataExtractor
from utils.flashing_frames_class import FlashingFrames
from utils.video_encoder_class import VideoEncoderFFMPEG
from utils.full_frame_annotator_class import FullFrameAnnotator

# Controller does not utilise threading logic, outputs will appear after entire logic is applied
# Acts as the master button controller used in the GUI
# Key assumptions for input folder structure:
# - The input folder contains images and a labels folder.
# - The labels folder contains .txt files for each image.

class CroppedMasterController:
    def __init__(self, window):
        self.window = window
        self.timings = []

        # Model paths are stored here for future expansion
        self.yolo_model_path = None  # Not used, placeholder for future YOLO integration in GUI, use external scripts on Kaggle to run Boxmot Tracker
        self.reid_model_path = None  # Not used, placeholder for future ReID integration in GUI, use external scripts on Kaggle to run Boxmot Tracker
        self.dlc_model_path = None   # Not used, placeholder for future ReID integration in GUI, use external scripts on Google Colab to run inference on videos with DLC

        self.connect_all()
        self.window.btn_process_all.clicked.connect(self.process_all)
        self.window.btn_cancel_process.clicked.connect(self.cancel_processing)
        self.window.btn_cancel_main.clicked.connect(self.cancel_and_close)


    # UX Functions
    # Ensures that the top row and "input parameter sets" are connected to slot functions
    def connect_all(self):
        for row in self.window.row_widgets:
            self.connect_row(row)
        self.window.le_yolo_model.textChanged.connect(self.refresh_buttons)
        self.window.le_reid_model.textChanged.connect(self.refresh_buttons)
        self.window.le_dlc_model.textChanged.connect(self.refresh_buttons)

    def connect_row(self, row):
        row["btn_input"].clicked.connect(lambda _, r=row: self.select_folder(r["le_input"]))
        row["btn_output"].clicked.connect(lambda _, r=row: self.select_folder(r["le_output"]))
        row["btn_process"].clicked.connect(lambda _, r=row: self.process_row(r))
        row["btn_remove"].clicked.connect(lambda _, r=row: self.clear_row(r))
        row["le_input"].textChanged.connect(self.refresh_buttons)
        row["le_output"].textChanged.connect(self.refresh_buttons)
        row["le_name"].textChanged.connect(self.refresh_buttons)

    # "Folder" selection buttons called this to open OS filesystem
    def select_folder(self, le_box):
        folder = QFileDialog.getExistingDirectory(self.window, "Select Folder", os.path.expanduser("~"))
        if folder:
            le_box.setText(folder)
            self.add_new_row_if_needed()
            self.refresh_buttons()

    # Checks whether to add new "input parameter set" updates and addws new input row
    def add_new_row_if_needed(self):
        for r in self.window.row_widgets:
            if not r["le_input"].text().strip() or not r["le_output"].text().strip():
                return
        new_row = self.window.add_input_row()
        self.connect_row(new_row)

    # Locking button logic to ensure buttons are locked when inputs are filled
    def refresh_buttons(self):
        for row in self.window.row_widgets:
            input_valid = bool(row["le_input"].text().strip())
            output_valid = bool(row["le_output"].text().strip())
            row["btn_process"].setEnabled(input_valid and output_valid)

        self.window.btn_process_all.setEnabled(
            any(
                row["le_input"].text().strip() and row["le_output"].text().strip() and row["le_name"].text().strip()
                for row in self.window.row_widgets
            )
        )

    def extract_inputs(self, row):
        return (
            row["le_input"].text().strip(),
            row["le_output"].text().strip(),
            row["le_name"].text().strip()
        )

    # Fucntion can be used to ensure inputs are entered, in this case it always returns true given that funcitionalilty doesn't actually work in GUI
    def validate_shared(self):
        self.yolo_model_path = self.window.le_yolo_model.text().strip()  # Variable to stored input in future
        self.reid_model_path = self.window.le_reid_model.text().strip()  # Variable to stored input in future
        self.dlc_model_path = self.window.le_dlc_model.text().strip()    # Variable to stored input in future
        return True

    # Functions for signal-lot functions for process buttons(when process buttons are pressed), UI will contain both a single "process all"  button at bottom 
    # and a single "process" button. Once pressed takes all valid inputs from each row and/or for that row respectivley and passes to run master function
    def process_row(self, row):
        self.validate_shared()

        input_folder, output_folder, folder_name = self.extract_inputs(row)
        if not input_folder or not output_folder or not folder_name:
            QMessageBox.warning(self.window, "Missing Input", "All fields must be filled.")
            return

        self.lock_controls()
        start = time.time()
        self.window.append_log(f"Running master pipeline for: {folder_name}")
        self.run_master(input_folder, output_folder, folder_name)
        elapsed = time.time() - start
        self.timings.append((row, input_folder, elapsed))
        self.handle_finished()
        self.unlock_controls()

    def process_all(self):
        self.validate_shared()

        self.lock_controls()
        self.timings = []
        self.window.append_log("Running master for valid input rows:")

        for i, row in enumerate(self.window.row_widgets, 1):
            input_folder, output_folder, folder_name = self.extract_inputs(row)
            if input_folder and output_folder and folder_name:
                self.window.append_log(f"[{i}] {folder_name}")
                start = time.time()
                self.run_master(input_folder, output_folder, folder_name)
                elapsed = time.time() - start
                self.timings.append((row, input_folder, elapsed))
            else:
                self.window.append_log(f"[{i}] Skipped: Incomplete row.")

        self.handle_finished()
        self.unlock_controls()
        self.window.append_log("Batch master processing finished.")


    # Main Master Logic which utilises the object creation from specific classes form utiles
    # Workflow:
    # 0. Creates new subfolders in output folder
    # 1. Copies demosaiced images from inputs to "Normal" folder
    # 2. Calls remove hidden files class to remove .xxxxx.png files and applies it to Normal folder
    # 3. Calls Bit depth converter class and applies to Normal folder and ensures images are 8 bit depth 
    # 4. Calls remove hidden files class to remove .xxxxx.png files and applies it to Normal folder again
    # 5. Copies labels folder (output from boxmot after applied to same images in input folder) to new labels folder
    # 6. Calls Larvae Cropper Class by matching .txt files and images files and crops and organises crops into appropriately named folders
    # 7. Calls Data extractor Class, which creates main csv file, getter functions called to store variables for
    # width res, height res, array of flashing indices
    # 8. Calls Flashing frames class to apply annotate frames to indicate flashing on the normal folder
    # 9. Calls video encoder class to create video from the normal full frame images
    # 10. Calls full frame annotator to annotate bounding box labels on normal images based on boxmot labels
    # and encodes these the images as well
    # 11. Annotates flashing frames and encodes images in cropped larvae folders
    # 12. Per larvae .CSV file created and copied from main .csv file
    # 13. Plots are created from per larcae .CSV file
    # 14. Final message of operation appended to text widget of GUI
    def run_master(self, input_path, output_root_path, folder_name):
        working_root = os.path.join(output_root_path, folder_name)
        normal = os.path.join(working_root, "Normal")
        label_dir = os.path.join(input_path, "labels")
        labels_out = os.path.join(working_root, "labels")
        larvae = os.path.join(working_root, "Cropped_Larvae")
        annotated = os.path.join(working_root, "Annotated")

        summary_lines = []

        try:
            self.window.append_log("1. Copying input files to Normal folder")
            os.makedirs(normal, exist_ok=True)
            for f in os.listdir(input_path):
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".json")):
                    shutil.copy(os.path.join(input_path, f), normal)

            self.window.append_log("2. Removing hidden files.")
            self.window.append_log(str(RemoveHiddenFiles(normal)()))

            self.window.append_log("3. Converting to 8-bit.")
            self.window.append_log(str(BitDepthConverter(normal, normal)()))

            self.window.append_log("4. Cleaning again after conversion.")
            self.window.append_log(str(RemoveHiddenFiles(normal)()))

            self.window.append_log("5. Copying existing labels folder to new labels folder")
            if not os.path.isdir(label_dir):
                self.window.append_log(f"Warning: 'labels' folder not found in {input_path}. Aborting remaining steps.")
                return
            os.makedirs(labels_out, exist_ok=True)
            for f in os.listdir(label_dir):
                if f.endswith(".txt"):
                    shutil.copy(os.path.join(label_dir, f), labels_out)

            self.window.append_log("6. Cropping larvae.")
            self.window.append_log(str(LarvaeObjectCropper(
                input_folder=labels_out,
                image_folder=normal,
                output_folder=larvae
            ).run()))

            self.window.append_log("7. Extracting CSV and flashing frames.")
            extractor = DataExtractor(normal, working_root)
            extractor.final_data_to_csv()

            main_csv_path = os.path.join(working_root, "main_data.csv")
            if not os.path.exists(main_csv_path):
                self.window.append_log("Warning: main_data.csv was not generated. Skipping downstream steps.")
                return

            flashing = extractor.get_flashing_frames()
            width = extractor.get_width()
            height = extractor.get_height()
            framerate = extractor.get_framerate()
            summary_lines.append(f"Resolution: {width} x {height}")
            summary_lines.append(f"Flashing Frame Indices: {flashing}")
            summary_lines.append(f"Framerate: {framerate}")

            self.window.append_log("8. Annotate flashing frames")
            self.window.append_log(str(FlashingFrames(normal, normal, flashing)()))

            self.window.append_log("9. Encoding full_frame.avi")
            self.window.append_log(str(
                VideoEncoderFFMPEG(normal, working_root, "full_frame", 8, framerate=framerate).run_command()
            ))

            self.window.append_log("10. Creating annotated frames.")
            self.window.append_log(str(FullFrameAnnotator(normal, labels_out, annotated)()))
            self.window.append_log(str(
                VideoEncoderFFMPEG(annotated, working_root, "annotated_full_frame", 8, framerate=framerate).run_command()
            ))

            self.window.append_log("11. Exporting larvae_xx CSVs.")
            extractor.larvae_data_exporter(main_csv_path, larvae)

            self.window.append_log("12. Annotating and plotting data per object.")
            for folder in os.listdir(larvae):
                full = os.path.join(larvae, folder)
                if folder.startswith("larvae_") and os.path.isdir(full):
                    object_id = folder.split("_")[-1]
                    object_csv_path = os.path.join(full, f"{object_id}_main_data.csv")

                    self.window.append_log(f" - Annotating flashing frames in {folder}")
                    self.window.append_log(str(FlashingFrames(full, full, flashing, outline_thickness=10)()))

                    if os.path.exists(object_csv_path):
                        self.window.append_log(f" - Plotting data for {object_id}")
                        extractor.larvae_data_plotter(object_csv_path, full)
                    else:
                        self.window.append_log(f"Skipped plot: {object_csv_path} not found.")

            self.window.append_log("13. Master complete.")
            for line in summary_lines:
                self.window.append_log(" - " + str(line))

        except Exception as e:
            self.window.append_log("Error during master pipeline:")
            self.window.append_log(str(e))
            self.window.append_log(traceback.format_exc())
            self.unlock_controls()

    # Additional UI/UX functions
    # Summary text 
    # Cancel Process buttons
    # Unocking/Locking features to handle button press logics, help reduce crashes for misuse of UX/UI
    # Clear buttons to reset input parameters
    def handle_finished(self):
        if self.timings:
            self.window.append_log("\nSummary of Processing Times:")
            for idx, (row, input_folder, elapsed) in enumerate(self.timings, 1):
                folder_name = os.path.basename(input_folder.rstrip("/"))
                self.window.append_log(f"Set {idx}: {folder_name} - ({elapsed:.2f} seconds)")

    def cancel_processing(self):
        self.window.append_log("Processing cancelled.")
        self.unlock_controls()

    def cancel_and_close(self):
        self.cancel_processing()
        self.window.close()

    def clear_row(self, row):
        if len(self.window.row_widgets) == 1:
            row["le_input"].clear()
            row["le_output"].clear()
            row["le_name"].clear()
            self.refresh_buttons()
            return
        row["container"].deleteLater()
        row["divider"].deleteLater()
        self.window.row_widgets.remove(row)
        self.refresh_buttons()

    def lock_controls(self):
        for row in self.window.row_widgets:
            row["btn_process"].setEnabled(False)
            row["btn_remove"].setEnabled(False)
        self.window.btn_process_all.setEnabled(False)
        self.window.btn_cancel_process.setEnabled(True)

    def unlock_controls(self):
        for row in self.window.row_widgets:
            row["btn_remove"].setEnabled(True)
        self.refresh_buttons()
        self.window.btn_cancel_process.setEnabled(False)
