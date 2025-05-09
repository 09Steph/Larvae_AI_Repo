import os
import time
from PySide6.QtWidgets import QFileDialog, QMessageBox
from controllers.thread_worker import ThreadWorker
from utils.bit_depth_convert_class import BitDepthConverter
from utils.folder_cleaner_class import FolderCleaner
from utils.flashing_frames_class import FlashingFrames
from utils.config_extractor_class import ConfigExtractor
from utils.json_copier_class import JsonCopier
from utils.remove_hidden_class import RemoveHiddenFiles

# Controller script used to control logic of extra processor button in UI
# Used to process images from the demosaiced images
# This script handles the extra processing of images, including copying configurations,
# Converting bit depth, cleaning folders and flashing frames

class ExtraProcessorController:
    def __init__(self, window):
        self.window = window
        self.active_workers = []
        self.running_processors = []
        self.task_queue = []
        self.current_task_index = 0
        self.cancelling = False
        self.timings = []
        self.connect_all()

        self.window.btn_process_all.clicked.connect(self.process_all)
        self.window.btn_cancel_process.clicked.connect(self.cancel_processing)
        self.window.btn_cancel_main.clicked.connect(self.cancel_and_close)

    def connect_all(self):
        for row in self.window.row_widgets:
            self.connect_row(row)

    def connect_row(self, row):
        row["btn_input_raw"].clicked.connect(lambda _, r=row: self.select_folder(r, "le_input_raw"))
        row["btn_input"].clicked.connect(lambda _, r=row: self.select_folder(r, "le_input"))
        row["btn_output"].clicked.connect(lambda _, r=row: self.select_folder(r, "le_output"))
        row["btn_process"].clicked.connect(lambda _, r=row: self.process_single_row(r))
        row["btn_remove"].clicked.connect(lambda _, r=row: self.remove_row(r))

    def select_folder(self, row, key):
        folder = QFileDialog.getExistingDirectory(self.window, "Select Folder", os.path.expanduser("~"))
        if folder:
            row[key].setText(folder)
            self.update_checkbox_enable_state(row)
            self.auto_add_new_row()

    def update_checkbox_enable_state(self, row):
        if row["le_input_raw"].text().strip():
            row["chk_copy_raw_configs"].setEnabled(True)
        else:
            row["chk_copy_raw_configs"].setChecked(False)
            row["chk_copy_raw_configs"].setEnabled(False)

        if row["le_input"].text().strip():
            row["chk_copy_inp_configs"].setEnabled(True)
        else:
            row["chk_copy_inp_configs"].setChecked(False)
            row["chk_copy_inp_configs"].setEnabled(False)

    def auto_add_new_row(self):
        for r in self.window.row_widgets:
            if not r["le_input_raw"].text() and not r["le_input"].text() and not r["le_output"].text():
                return
        self.connect_row(self.window.add_input_row())

    def validate_row(self, row):
        input_folder = row["le_input"].text().strip()
        output_folder = row["le_output"].text().strip()
        return input_folder and output_folder

    def process_all(self):
        self.timings = []
        self.window.btn_process_all.setEnabled(False)
        self.window.btn_cancel_process.setEnabled(True)
        self.lock_individual_processes()

        sets = []
        for row in self.window.row_widgets:
            if self.validate_row(row):
                sets.append(row)

        if not sets:
            self.unlock_individual_processes()
            self.window.btn_process_all.setEnabled(True)
            self.window.btn_cancel_process.setEnabled(False)
            return

        for row in sets:
            self.prepare_task_queue(row)
        self.start_next_task()

    def process_single_row(self, row):
        self.timings = []
        self.window.btn_process_all.setEnabled(False)
        self.window.btn_cancel_process.setEnabled(True)
        self.lock_individual_processes()
        row["btn_process"].setEnabled(False)

        self.prepare_task_queue(row)
        self.start_next_task()

    def prepare_task_queue(self, row):
        self.processor_set_timings = []
        self.task_queue.clear()
        self.current_task_index = 0

        input_raw = row["le_input_raw"].text().strip()
        input_folder = row["le_input"].text().strip()
        output_folder = row["le_output"].text().strip()

        self.flashing_frames = []

        if input_folder:
            self.task_queue.append(("Remove Hidden (Input)", RemoveHiddenFiles(input_folder)))

        if row["chk_copy_raw_configs"].isChecked() and input_raw:
            self.task_queue.append(("Copy Configs (Raw)", JsonCopier(input_raw, output_folder)))

        if row["chk_copy_inp_configs"].isChecked():
            self.task_queue.append(("Copy Configs (Input)", JsonCopier(input_folder, output_folder)))

        if row["chk_convert_8bit"].isChecked():
            self.task_queue.append(("Convert to 8-bit", BitDepthConverter(input_folder, output_folder)))

        self.task_queue.append(("Remove Hidden (After Copy/Conversion)", RemoveHiddenFiles(output_folder)))
        self.task_queue.append(("Folder Cleaner", FolderCleaner(output_folder)))

        extractor = ConfigExtractor(output_folder)
        def config_extraction_task():
            extractor.run()
            self.config_data = extractor.get_config_data()
            self.flashing_frames = extractor.get_flashing_frames()
        self.task_queue.append(("Extract Configs", config_extraction_task))

        def flashing_frames_task():
            flash = FlashingFrames(output_folder, output_folder, self.flashing_frames)
            flash()
        self.task_queue.append(("Flashing Frames", flashing_frames_task))

        self.task_queue.append(("Final Remove Hidden", RemoveHiddenFiles(output_folder)))

    def start_next_task(self):
        if self.current_task_index >= len(self.task_queue):
            self.processing_done()
            return

        step_name, task = self.task_queue[self.current_task_index]
        self.running_processors.append(task)
        worker = ThreadWorker(self.run_and_time, task, step_name)
        worker.log_signal.connect(self.window.append_log)
        worker.finished_signal.connect(lambda result, elapsed, name=step_name: self.finish_task(name, elapsed))
        self.active_workers.append(worker)
        worker.start()

    def finish_task(self, step_name, elapsed_time):
        self.processor_set_timings.append((step_name, elapsed_time))

        self.current_task_index += 1
        self.start_next_task()

    def processing_done(self):
        self.window.append_log("\nSummary of Processing Times:")
        total = 0
        for idx, (name, elapsed) in enumerate(self.processor_set_timings, 1):
            self.window.append_log(f"Step {idx} ({name}): {elapsed:.2f} seconds")
            total += elapsed
        self.window.append_log(f"Total Time for Set: {total:.2f} seconds\n")
        self.window.append_log(self.window.initial_text)

        self.active_workers.clear()
        self.running_processors.clear()
        self.window.btn_process_all.setEnabled(True)
        self.window.btn_cancel_process.setEnabled(False)
        self.unlock_individual_processes()

    def run_and_time(self, processor_obj, step_name):
        start = time.perf_counter()
        if callable(processor_obj):
            processor_obj()
        else:
            processor_obj()
        end = time.perf_counter()
        elapsed = end - start
        return None, elapsed

    def cancel_processing(self):
        self.window.append_log("\nCancelling processing")
        self.cancelling = True
        for processor in self.running_processors:
            if hasattr(processor, "stop"):
                processor.stop()

        self.window.btn_process_all.setEnabled(True)
        self.window.btn_cancel_process.setEnabled(False)
        self.unlock_individual_processes()

    def cancel_and_close(self):
        self.cancel_processing()
        self.window.close()

    def remove_row(self, row):
        container = row["container"]
        divider = row["divider"]
        container.deleteLater()
        divider.deleteLater()

        if row in self.window.row_widgets:
            self.window.row_widgets.remove(row)

    def lock_individual_processes(self):
        for row in self.window.row_widgets:
            row["btn_process"].setEnabled(False)
            row["btn_remove"].setEnabled(False)

    def unlock_individual_processes(self):
        for row in self.window.row_widgets:
            input_folder_filled = bool(row["le_input"].text().strip())
            output_folder_filled = bool(row["le_output"].text().strip())
            ready = input_folder_filled and output_folder_filled
            row["btn_process"].setEnabled(ready)
            row["btn_remove"].setEnabled(True)
