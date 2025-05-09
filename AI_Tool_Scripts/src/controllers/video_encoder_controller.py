import os
import time
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QProcess
from utils.video_encoder_class import VideoEncoderFFMPEG

class VideoEncoderController:
    def __init__(self, window):
        self.window = window
        self.active_processes = []
        self.running_encodings = {}
        self.timings = []
        self.cancelling = False
        self.connect_all()

        self.window.btn_encode_all.clicked.connect(self.encode_all)
        self.window.btn_cancel_process.clicked.connect(self.cancel_processing)
        self.window.btn_cancel_main.clicked.connect(self.cancel_and_close)

    def connect_all(self):
        for row in self.window.video_sets:
            self.connect_row(row)

    def connect_row(self, row):
        row["btn_input"].clicked.connect(lambda _, r=row: self.select_folder(r["le_input"], r))
        row["btn_output"].clicked.connect(lambda _, r=row: self.select_folder(r["le_output"], r))
        row["cb_8bit"].stateChanged.connect(lambda _, r=row: self.toggle_bit_depth(r["cb_8bit"], r["cb_16bit"]))
        row["cb_16bit"].stateChanged.connect(lambda _, r=row: self.toggle_bit_depth(r["cb_16bit"], r["cb_8bit"]))
        row["btn_encode"].clicked.connect(lambda _, r=row: self.encode_single(r))
        row["btn_remove"].clicked.connect(lambda _, r=row: self.remove_row(r))

    def select_folder(self, le_box, row=None):
        folder = QFileDialog.getExistingDirectory(self.window, "Select Folder", os.path.expanduser("~"))
        if folder:
            le_box.setText(folder)
            if row and not self.has_empty_row():
                new_row = self.window.add_video_set_row()
                self.connect_row(new_row)

    def has_empty_row(self):
        for row in self.window.video_sets:
            if not row["le_input"].text() and not row["le_output"].text() and not row["le_name"].text():
                return True
        return False

    def toggle_bit_depth(self, selected, other):
        if selected.isChecked():
            other.setChecked(False)

    def validate_row(self, row):
        input_folder = row["le_input"].text().strip()
        output_folder = row["le_output"].text().strip()
        output_name = row["le_name"].text().strip()
        bit_selected = row["cb_8bit"].isChecked() or row["cb_16bit"].isChecked()
        return all([input_folder, output_folder, output_name, bit_selected])

    def lock_all_encodes(self):
        self.window.btn_encode_all.setEnabled(False)
        for row in self.window.video_sets:
            row["btn_encode"].setEnabled(False)
            row["btn_remove"].setEnabled(False)

    def unlock_all_encodes(self):
        self.window.btn_encode_all.setEnabled(True)
        for row in self.window.video_sets:
            ready = self.validate_row(row)
            row["btn_encode"].setEnabled(ready)
            row["btn_remove"].setEnabled(True)

    def encode_all(self):
        if self.cancelling:
            return

        complete_rows = [r for r in self.window.video_sets if self.validate_row(r)]

        if not complete_rows:
            QMessageBox.warning(self.window, "Missing Inputs", "No complete parameter sets to encode.")
            return

        self.lock_all_encodes()
        self.window.btn_cancel_process.setEnabled(True)

        for row in complete_rows:
            self.start_encoding(row)

    def encode_single(self, row):
        if self.cancelling:
            return

        if not self.validate_row(row):
            QMessageBox.warning(self.window, "Missing Inputs", "Please fill in all parameters and select bit depth.")
            return

        self.lock_all_encodes()
        self.window.btn_cancel_process.setEnabled(True)

        self.start_encoding(row)

    def start_encoding(self, row):
        input_folder = row["le_input"].text().strip()
        output_folder = row["le_output"].text().strip()
        output_name = row["le_name"].text().strip()
        bit_depth = 8 if row["cb_8bit"].isChecked() else 16
        framerate_text = row["le_framerate"].text().strip()
        framerate = int(framerate_text) if framerate_text else 10

        encoder = VideoEncoderFFMPEG(
            input_folder=input_folder,
            output_folder=output_folder,
            output_file_name=output_name,
            bit_depth=bit_depth,
            framerate=framerate
        )

        try:
            cmd = encoder.build_command_normal()
            self.window.append_log(f"\nRunning ffmpeg command:\n{' '.join(cmd)}")

            process = QProcess(self.window)
            process.setProcessChannelMode(QProcess.MergedChannels)
            process.readyReadStandardOutput.connect(lambda p=process: self.read_output(p))
            process.readyReadStandardError.connect(lambda p=process: self.read_output(p))
            process.finished.connect(lambda: self.process_finished(process, output_name))

            self.active_processes.append(process)
            self.running_encodings[process] = time.perf_counter(), output_name
            process.start(cmd[0], cmd[1:])

        except Exception as e:
            QMessageBox.critical(self.window, "Encoding Error", f"Encoder Error: {e}")

    def read_output(self, process):
        data = process.readAllStandardOutput().data().decode()
        if data:
            self.window.append_log(data.strip())

    def process_finished(self, process, output_name):
        if process in self.active_processes:
            start_time, name = self.running_encodings.pop(process)
            elapsed_time = time.perf_counter() - start_time
            self.timings.append((name, elapsed_time))

            self.active_processes.remove(process)

        if not self.active_processes:
            self.window.btn_cancel_process.setEnabled(False)
            self.unlock_all_encodes()
            self.cancelling = False
            self.append_summary()

    def append_summary(self):
        self.window.append_log("\nSummary of Encodings:")
        for idx, (name, elapsed) in enumerate(self.timings, 1):
            self.window.append_log(f"Set {idx}: {name} - ({elapsed:.2f} seconds)")

    def cancel_processing(self):
        if self.active_processes:
            for process in self.active_processes:
                process.kill()
            self.active_processes.clear()
            self.running_encodings.clear()
            self.window.btn_cancel_process.setEnabled(False)
            self.unlock_all_encodes()
            self.window.append_log("\nEncoding cancelled.")
            self.cancelling = True

    def cancel_and_close(self):
        self.cancel_processing()
        self.window.close()

    def remove_row(self, row):
        if len(self.window.video_sets) == 1:
            row["le_input"].clear()
            row["le_output"].clear()
            row["le_name"].clear()
            row["le_framerate"].clear()
            row["cb_8bit"].setChecked(False)
            row["cb_16bit"].setChecked(False)
            return

        container = row["container"]
        divider = row["divider"]
        container.deleteLater()
        divider.deleteLater()

        if row in self.window.video_sets:
            self.window.video_sets.remove(row)
