import os
import subprocess

# Class used to raw data frames using libcamera-raw 
# Passes command termanial as a subprocess

class LibCameraRawCapture:
    def __init__(self, mode="4056:3040:12:U", roi="0,0,1,1",
                 timeout=35000, output_dir="/media/steph/DataSSD", filename="frame_%05d.raw",
                 segment=1, framerate=10, shutter_speed=None, gain=None, verbose=True):
      
        self.mode = mode     # Allow you to select the mode of the camera (resolution, bit depth)
        self.roi = roi   # Allows you to select effective Region of interest (x,y,width,height) - in this case the whole image
        self.timeout = timeout  # Capture duration in milliseconds
        self.output_dir = output_dir    # Output directory where the images will be saved
        self.filename = filename    # Output file name pattern
        self.segment = segment  # Number of segments/files, essentially 1 frame per file
        self.framerate = framerate  # FPS
        self.shutter_speed = shutter_speed  # Shutter speed in microseconds
        self.gain = gain    # Analog gain value
        self.verbose = verbose  # Debugging statements of the command - very useful for seeing how the command sets up and identify number of frmaes captured/any frame drops

        if not os.path.exists(self.output_dir):
            print(f"Folder '{self.output_dir}' does not exist - Creating new folder")
            os.makedirs(self.output_dir)
        self.output = os.path.join(self.output_dir, self.filename)

    def build_command(self):
        cmd = [
            "libcamera-raw",
            "--mode", self.mode,
            "--roi", self.roi,
            "-t", str(self.timeout),
            "--output", self.output,
            "--segment", str(self.segment)
        ]
        if self.verbose:
            cmd.append("--verbose")
        if self.framerate is not None:
            cmd.extend(["--framerate", str(self.framerate)])
        if self.shutter_speed is not None:
            cmd.extend(["--shutter", str(self.shutter_speed)])
        if self.gain is not None:
            cmd.extend(["--gain", str(self.gain)])
        return cmd

    def get_command_str(self):
        return " ".join(self.build_command())

    def capture(self):
        cmd = self.build_command()
        print("Executing command:", " ".join(cmd))
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    capture = LibCameraRawCapture()
    capture.capture()

