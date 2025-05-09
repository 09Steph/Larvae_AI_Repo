import os
import subprocess
import cv2

# Class to encode images into a video using FFMPEG
# Workflow:
# 1. Initialize the class with input and output folder paths, output file name, bit depth, and framerate.
# 2. Create the output folder if it doesn't exist.
# 3. Method to stop processing.
# 4. Derive the input pattern for the images based on their filenames.
# 5. Build the FFMPEG command to encode the images into a video.
# 6. Run the FFMPEG command to create the video.
# 7. Handle errors during the encoding process.

# Notes:
# Assumes the input images are named in a specific format (e.g., "frame_00001.png").
# The class uses FFMPEG to encode the images into a video file with the specified bit depth and framerate.
# Encoder is lossless codec called FFV1.
# Pixle format is set to yuv420p for 8-bit depth and yuv422p16le for 16-bit depth.

class VideoEncoderFFMPEG:
    def __init__(self, input_folder, output_folder, output_file_name,
                 bit_depth, framerate=10):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.output_file_name = output_file_name
        self.bit_depth = bit_depth
        self.framerate = framerate
        self.should_stop = False
        os.makedirs(self.output_folder, exist_ok=True)

    def stop(self):
        self.should_stop = True

    def derive_input_pattern(self):
        for fname in os.listdir(self.input_folder):
            name, ext = os.path.splitext(fname)
            ext_low = ext.lower()
            if ext_low not in (".png", ".jpg", ".jpeg", ".tif", ".tiff"):
                continue
            if len(name) < 11:
                continue
            suffix = name[-11:]
            if suffix.startswith("frame_") and suffix[6:].isdigit():
                prefix = name[:-11]
                return os.path.join(
                    self.input_folder,
                    f"{prefix}frame_%05d{ext}"
                )
        raise FileNotFoundError("No files ending with 'frame_#####.<ext>' found")

    def build_command_normal(self):
        inp_pattern = self.derive_input_pattern()
        out_name = self.output_file_name
        if not out_name.lower().endswith(".avi"):
            out_name += ".avi"
        out_path = os.path.join(self.output_folder, out_name)

        pix_fmt = "yuv420p" if self.bit_depth == 8 else "yuv422p16le"

        return [
            "ffmpeg",
            "-framerate", str(self.framerate),
            "-i", inp_pattern,
            "-c:v", "ffv1",
            "-pix_fmt", pix_fmt,
            out_path
        ]

    def run_command(self):
        if self.should_stop:
            print("Encoding canceled before starting ffmpeg.")
            return

        try:
            cmd = self.build_command_normal()
            print("Running:", " ".join(cmd))
            subprocess.run(cmd, check=True)
            print(f"Encoded video saved to: {cmd[-1]}")
        except subprocess.CalledProcessError as e:
            print(f"Error running ffmpeg: {e}")
        except FileNotFoundError as e:
            print(f"Pattern error: {e}")
