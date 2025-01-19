import os
import time
import shutil
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Folder paths
CAMERA_FOLDER = "camera_pictures"
UPLOADED_FOLDER = "uploaded"
UPLOAD_URL = "https://projects.benax.rw/f/o/x/e/a/c/h/p/x/o/j/e/c/t/s/4e8d42b606T70Ta9d39741a93ed0356c/iot_testing_202501/upload.php"

# This ensures required folders exist
os.makedirs(CAMERA_FOLDER, exist_ok=True)
os.makedirs(UPLOADED_FOLDER, exist_ok=True)

# event handler
class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.jpg', '.png')):
            self.process_image(event.src_path)
    
    def process_image(self, image_path):
        print(f"New image detected: {image_path}")
        time.sleep(30)  # Wait for 30 seconds
        
        try:
            # Uploading the image using curl
            print(f"Uploading {image_path}...")
            result = subprocess.run(
                ["curl", "-X", "POST", "-F", f"imageFile=@{image_path}", UPLOAD_URL],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"Upload successful: {image_path}")
                self.move_image(image_path)
            else:
                print(f"Failed to upload {image_path}: {result.stderr}")
        except Exception as e:
            print(f"Error while uploading {image_path}: {e}")
    
    def move_image(self, image_path):
        # Move the uploaded image to the 'uploaded' folder
        filename = os.path.basename(image_path)
        destination = os.path.join(UPLOADED_FOLDER, filename)
        shutil.move(image_path, destination)
        print(f"Moved {image_path} to {destination}")

# Set up the folder observer
observer = Observer()
handler = ImageHandler()
observer.schedule(handler, path=CAMERA_FOLDER, recursive=False)

print(f"Monitoring folder: {CAMERA_FOLDER}")
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
