import subprocess

# Class used to check/view the camera feed

class CameraCheck:
    def __init__(self, command="libcamera-vid -t 0"):
        self.command = command

    def run(self):
        process = subprocess.Popen(self.command.split())
        return process

if __name__ == "__main__":
    camera = CameraCheck()
    camera.run()
