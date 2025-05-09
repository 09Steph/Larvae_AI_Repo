import os
from PySide6.QtWidgets import QFileDialog, QMessageBox
from controllers.thread_worker import ThreadWorker
from utils.petri_dish_cropper_circle_class import PetriDishCropperCircle
from utils.petri_dish_cropper_view_class import PetriDishCropperView

# Notes:
# Controller script used to control logic of cropper button in UI
# Used to crop images from the demosaiced images

class CropperController:
    def __init__(self, window):
        self.window = window
        self.active_workers = []
        self.running_croppers = []
        self.cancelling = False
        self.connect_all()

        self.window.btn_crop.clicked.connect(self.process_all)
        self.window.btn_cancel_process.clicked.connect(self.cancel_processing)
        self.window.btn_cancel_main.clicked.connect(self.cancel_and_close)

    def connect_all(self):
        for row in self.window.row_widgets:
            self.connect_row(row)

    def connect_row(self, row):
        row["btn_input"].clicked.connect(lambda _, r=row: self.select_folder(r["le_input"], r))
        row["btn_output"].clicked.connect(lambda _, r=row: self.select_folder(r["le_output"], r))
        row["btn_crop"].clicked.connect(lambda _, r=row: self.process_single_row(r))
        row["btn_view"].clicked.connect(lambda _, r=row: self.view_crop(r))
        row["btn_remove"].clicked.connect(lambda _, r=row: self.remove_row(r))
        row["btn_crop"].setEnabled(False)

    def select_folder(self, le_box, row):
        folder = QFileDialog.getExistingDirectory(self.window, "Select Folder", os.path.expanduser("~"))
        if folder:
            le_box.setText(folder)
            self.update_crop_button_state(row)
            self.add_new_row_if_needed()
            self.update_crop_all_state()

    def update_crop_button_state(self, row):
        input_filled = bool(row["le_input"].text().strip())
        output_filled = bool(row["le_output"].text().strip())
        row["btn_crop"].setEnabled(input_filled and output_filled)

    def update_crop_all_state(self):
        any_ready = any(
            r["le_input"].text().strip() and r["le_output"].text().strip()
            for r in self.window.row_widgets
        )
        self.window.btn_crop.setEnabled(any_ready)

    def add_new_row_if_needed(self):
        for r in self.window.row_widgets:
            if not r["le_input"].text() or not r["le_output"].text():
                return
        new_row = self.window.add_input_row()
        self.connect_row(new_row)

    def view_crop(self, row):
        input_folder = row["le_input"].text().strip()
        x = row["le_x"].text().strip()
        y = row["le_y"].text().strip()
        radius = row["le_radius"].text().strip()

        if not input_folder or not (x and y and radius):
            QMessageBox.warning(self.window, "Missing Info", "Please select Input Folder and enter X/Y/Radius.")
            return

        try:
            viewer = PetriDishCropperView(input_folder, int(x), int(y), int(radius))
            viewer()
        except Exception as e:
            QMessageBox.critical(self.window, "Error Viewing Crop", f"An error occurred: {e}")

    def process_all(self):
        defaults = {"x": 2028, "y": 1420, "radius": 1200}
        self.timings = []
        sets = []
        errors = []
        self.cancelling = False

        self.window.btn_crop.setEnabled(False)
        self.window.btn_cancel_process.setEnabled(True)
        self.lock_individual_crops()
        self.lock_all_removes()

        for i, row in enumerate(self.window.row_widgets, start=1):
            input_folder = row["le_input"].text().strip()
            output_folder = row["le_output"].text().strip()

            input_filled = bool(input_folder)
            output_filled = bool(output_folder)

            if (input_filled and not output_filled) or (output_filled and not input_filled):
                errors.append(f"Set {i}")
                continue

            if not (input_filled or output_filled):
                continue

            x = row["le_x"].text().strip()
            y = row["le_y"].text().strip()
            radius = row["le_radius"].text().strip()

            x_val = int(x or defaults["x"])
            y_val = int(y or defaults["y"])
            radius_val = int(radius or defaults["radius"])

            sets.append((row, input_folder, output_folder, x_val, y_val, radius_val))

        if errors:
            QMessageBox.warning(
                self.window,
                "Missing Info",
                f"Missing Input or Output folder in: {', '.join(errors)}"
            )

        if not sets:
            self.unlock_individual_crops()
            self.unlock_all_removes()
            self.window.btn_crop.setEnabled(True)
            self.window.btn_cancel_process.setEnabled(False)
            return

        for row, input_folder, output_folder, x, y, radius in sets:
            self.start_crop(row, input_folder, output_folder, x, y, radius)

    def process_single_row(self, row):
        defaults = {"x": 2028, "y": 1420, "radius": 1200}
        self.cancelling = False
        self.timings = []

        input_folder = row["le_input"].text().strip()
        output_folder = row["le_output"].text().strip()

        if not input_folder or not output_folder:
            QMessageBox.warning(self.window, "Missing Info", "Both Input and Output folders are required.")
            return

        x = row["le_x"].text().strip()
        y = row["le_y"].text().strip()
        radius = row["le_radius"].text().strip()

        x_val = int(x or defaults["x"])
        y_val = int(y or defaults["y"])
        radius_val = int(radius or defaults["radius"])

        self.window.btn_crop.setEnabled(False)
        self.window.btn_cancel_process.setEnabled(True)
        self.lock_individual_crops()
        self.lock_all_removes()
        row["btn_crop"].setEnabled(False)

        self.start_crop(row, input_folder, output_folder, x_val, y_val, radius_val)

    def start_crop(self, row, input_folder, output_folder, x, y, radius):
        def run_crop(input_folder, output_folder, x, y, radius, cropper):
            cropper()

        cropper = PetriDishCropperCircle(input_folder, output_folder, x, y, radius)
        self.running_croppers.append(cropper)

        worker = ThreadWorker(run_crop, input_folder, output_folder, x, y, radius, cropper)
        worker.log_signal.connect(self.window.append_log)
        worker.finished_signal.connect(lambda result, elapsed: self.handle_finished(row, input_folder, elapsed))
        self.active_workers.append(worker)
        worker.start()

    def handle_finished(self, row, input_folder, elapsed_time):
        self.timings.append((row, input_folder, elapsed_time))

        if all(not w.isRunning() for w in self.active_workers):
            if self.cancelling:
                self.window.append_log("\nCrop process was cancelled.")
            else:
                self.window.append_log("\nSummary of Processing Times:")
                for idx, (row, input_folder, elapsed) in enumerate(self.timings, 1):
                    folder_name = os.path.basename(input_folder.rstrip("/"))
                    self.window.append_log(f"Set {idx}: {folder_name} - ({elapsed:.2f} seconds)")

            self.active_workers.clear()
            self.running_croppers.clear()
            self.window.btn_crop.setEnabled(True)
            self.window.btn_cancel_process.setEnabled(False)
            self.unlock_individual_crops()
            self.unlock_all_removes()

    def cancel_processing(self):
        if self.running_croppers:
            self.window.append_log("\nCancelling cropping")
            self.cancelling = True
            for cropper in self.running_croppers:
                cropper.stop()

        self.window.btn_crop.setEnabled(True)
        self.window.btn_cancel_process.setEnabled(False)
        self.unlock_individual_crops()
        self.unlock_all_removes()

    def cancel_and_close(self):
        self.cancel_processing()
        self.window.close()

    def remove_row(self, row):
        if len(self.window.row_widgets) == 1:
            row["le_input"].clear()
            row["le_output"].clear()
            row["le_x"].clear()
            row["le_y"].clear()
            row["le_radius"].clear()
            return

        container = row["container"]
        divider = row["divider"]
        container.deleteLater()
        divider.deleteLater()

        if row in self.window.row_widgets:
            self.window.row_widgets.remove(row)

        self.add_new_row_if_needed()
        self.update_crop_all_state()

    def lock_individual_crops(self):
        for row in self.window.row_widgets:
            row["btn_crop"].setEnabled(False)

    def unlock_individual_crops(self):
        for row in self.window.row_widgets:
            self.update_crop_button_state(row)

    def lock_all_removes(self):
        for row in self.window.row_widgets:
            row["btn_remove"].setEnabled(False)

    def unlock_all_removes(self):
        for row in self.window.row_widgets:
            row["btn_remove"].setEnabled(True)
