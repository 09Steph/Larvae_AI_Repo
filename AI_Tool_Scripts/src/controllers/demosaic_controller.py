import os
from PySide6.QtWidgets import QFileDialog, QMessageBox
from controllers.thread_worker import ThreadWorker
from utils.raw_to_16_class import RawTo16

# Controller script used to control logic of demosaic button in UI
# Used to demosaic images from the raw images

class DemosaicController:
    def __init__(self, window):
        self.window = window
        self.active_workers = []
        self.running_demosaics = []
        self.cancelling = False

        self.connect_all()

        self.window.btn_demosaic.clicked.connect(self.process_all)
        self.window.btn_cancel_process.clicked.connect(self.cancel_processing)
        self.window.btn_cancel_main.clicked.connect(self.cancel_and_close)

    def connect_all(self):
        for row in self.window.row_widgets:
            self.connect_row(row)

    def connect_row(self, row):
        row["btn_input"].clicked.connect(lambda _, r=row: self.select_folder(r["le_input"]))
        row["btn_output"].clicked.connect(lambda _, r=row: self.select_folder(r["le_output"]))
        row["btn_demosaic"].clicked.connect(lambda _, r=row: self.process_single_row(r))
        row["btn_remove"].clicked.connect(lambda _, r=row: self.remove_row(r))

    def select_folder(self, le_box):
        folder = QFileDialog.getExistingDirectory(self.window, "Select Folder", os.path.expanduser("~"))
        if folder:
            le_box.setText(folder)
            self.add_new_row_if_needed()

    def add_new_row_if_needed(self):
        for r in self.window.row_widgets:
            if not r["le_input"].text() or not r["le_output"].text():
                return
        new_row = self.window.add_input_row()
        self.connect_row(new_row)

    def process_all(self):
        defaults = {"width": 4056, "height": 3040, "stride_bytes": 8128}
        self.timings = []
        sets = []
        errors = []
        self.cancelling = False

        self.window.btn_demosaic.setEnabled(False)
        self.window.btn_cancel_process.setEnabled(True)
        self.lock_individual_demosaics()
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

            width = int(row["le_width"].text().strip() or defaults["width"])
            height = int(row["le_height"].text().strip() or defaults["height"])
            stride_bytes = int(row["le_stride"].text().strip() or defaults["stride_bytes"])

            sets.append((row, input_folder, output_folder, width, height, stride_bytes))

        if errors:
            QMessageBox.warning(
                self.window,
                "Missing Info",
                f"Incomplete folder selection in: {', '.join(errors)}"
            )

        if not sets:
            self.unlock_individual_demosaics()
            self.unlock_all_removes()
            self.window.btn_demosaic.setEnabled(True)
            self.window.btn_cancel_process.setEnabled(False)
            return

        for row, input_folder, output_folder, width, height, stride_bytes in sets:
            self.start_demosaic(row, input_folder, output_folder, width, height, stride_bytes)

    def process_single_row(self, row):
        defaults = {"width": 4056, "height": 3040, "stride_bytes": 8128}
        self.cancelling = False
        self.timings = []

        input_folder = row["le_input"].text().strip()
        output_folder = row["le_output"].text().strip()

        if not input_folder or not output_folder:
            QMessageBox.warning(self.window, "Missing Info", "Both Input and Output folders are required.")
            return

        width = int(row["le_width"].text().strip() or defaults["width"])
        height = int(row["le_height"].text().strip() or defaults["height"])
        stride_bytes = int(row["le_stride"].text().strip() or defaults["stride_bytes"])

        self.window.btn_demosaic.setEnabled(False)
        self.window.btn_cancel_process.setEnabled(True)
        self.lock_individual_demosaics()
        self.lock_all_removes()
        row["btn_demosaic"].setEnabled(False)

        self.start_demosaic(row, input_folder, output_folder, width, height, stride_bytes)

    def start_demosaic(self, row, input_folder, output_folder, width, height, stride_bytes):
        def run_demosaic(input_folder, output_folder, width, height, stride_bytes, demosaic_obj):
            demosaic_obj()

        demosaic_obj = RawTo16(input_folder, output_folder, width, height, stride_bytes)
        self.running_demosaics.append(demosaic_obj)

        worker = ThreadWorker(run_demosaic, input_folder, output_folder, width, height, stride_bytes, demosaic_obj)
        worker.log_signal.connect(self.window.append_log)
        worker.finished_signal.connect(lambda result, elapsed: self.handle_finished(row, input_folder, elapsed))
        self.active_workers.append(worker)
        worker.start()

    def handle_finished(self, row, input_folder, elapsed_time):
        self.timings.append((row, input_folder, elapsed_time))

        if all(not w.isRunning() for w in self.active_workers):
            if self.cancelling:
                self.window.append_log("\nDemosaic process was cancelled.")
            else:
                self.window.append_log("\nSummary of Processing Times:")
                for idx, (row, input_folder, elapsed) in enumerate(self.timings, 1):
                    folder_name = os.path.basename(input_folder.rstrip("/"))
                    self.window.append_log(f"Set {idx}: {folder_name} - ({elapsed:.2f} seconds)")

            self.active_workers.clear()
            self.running_demosaics.clear()
            self.window.btn_demosaic.setEnabled(True)
            self.window.btn_cancel_process.setEnabled(False)
            self.unlock_individual_demosaics()
            self.unlock_all_removes()

    def cancel_processing(self):
        if self.running_demosaics:
            self.window.append_log("\nCancelling demosaicing")
            self.cancelling = True
            for demosaic_obj in self.running_demosaics:
                demosaic_obj.stop()

        self.window.btn_demosaic.setEnabled(True)
        self.window.btn_cancel_process.setEnabled(False)
        self.unlock_individual_demosaics()
        self.unlock_all_removes()

    def cancel_and_close(self):
        self.cancel_processing()
        self.window.close()

    def remove_row(self, row):
        if len(self.window.row_widgets) == 1:
            row["le_input"].clear()
            row["le_output"].clear()
            row["le_width"].clear()
            row["le_height"].clear()
            row["le_stride"].clear()
            return

        container = row["container"]
        divider = row["divider"]
        container.deleteLater()
        divider.deleteLater()

        if row in self.window.row_widgets:
            self.window.row_widgets.remove(row)

        self.add_new_row_if_needed()

    def lock_individual_demosaics(self):
        for row in self.window.row_widgets:
            row["btn_demosaic"].setEnabled(False)

    def unlock_individual_demosaics(self):
        for row in self.window.row_widgets:
            input_filled = bool(row["le_input"].text().strip())
            output_filled = bool(row["le_output"].text().strip())
            row["btn_demosaic"].setEnabled(input_filled and output_filled)

    def lock_all_removes(self):
        for row in self.window.row_widgets:
            row["btn_remove"].setEnabled(False)

    def unlock_all_removes(self):
        for row in self.window.row_widgets:
            row["btn_remove"].setEnabled(True)
