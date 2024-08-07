import threading
import queue
import os
import cv2
import time
from datetime import datetime
from PIL import Image, ImageTk
import numpy as np
from pypylon import pylon


class ImageSaverHandler(pylon.ImageEventHandler):
    def __init__(
        self,
        save_queue: queue.Queue,
        display_queue: queue.Queue,
        recording_event: threading.Event,
    ):
        super().__init__()
        self.save_queue = save_queue
        self.display_queue = display_queue
        self.recording_event = recording_event

    def OnImageGrabbed(self, camera, grabResult):
        if grabResult.GrabSucceeded():
            img = grabResult.Array
            # timestamp = str(datetime.now().timestamp()).format(".5f")
            timestamp = "{:.5f}".format(datetime.now().timestamp())
            # print(timestamp)
            # Put copies into both queues
            if self.recording_event.is_set():
                self.save_queue.put((np.copy(img), timestamp))
            # Ensure only the latest frame is in the queue
            if not self.display_queue.empty():
                try:
                    self.display_queue.get_nowait()
                except queue.Empty:
                    pass
            self.display_queue.put((np.copy(img), timestamp))
        grabResult.Release()


def save_image_async(
    folder: str, recording_event: threading.Event, save_queue: queue.Queue
):
    while recording_event.is_set() or not save_queue.empty():
        img, timestamp = save_queue.get()
        if img is None:
            continue
        image_pil = Image.fromarray(img)
        filename = os.path.join(folder, f"image_{timestamp}.bmp")
        image_pil.save(filename)
        print(f"Image saved as {filename}")


def capture_webcam_frames(
    camera: cv2.VideoCapture,
    stop_camera_event: threading.Event,
    display_queue: queue.Queue,
    save_queue: queue.Queue,
    record_event: threading.Event,
    fps: int = 30,
):
    while not stop_camera_event.is_set():
        ret, frame = camera.read()
        if ret:
            frame = cv2.flip(frame, 1)
            raw_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            timestamp = str(datetime.now().timestamp())
            # Put copies into both queues
            if record_event.is_set():
                save_queue.put((np.copy(raw_image), timestamp))
            # Ensure only the latest frame is in the queue
            if not display_queue.empty():
                try:
                    display_queue.get_nowait()
                except queue.Empty:
                    pass
            display_queue.put((np.copy(raw_image), timestamp))
        time.sleep(1 / fps)


class Camera:
    def __init__(self, type="webcam", fps=70):
        self.type = type
        self.save_queue = queue.Queue()
        self.display_queue = queue.Queue()
        self.stop_camera_event = threading.Event()
        self.record_event = threading.Event()
        self.saver_thread = None
        self.camera = None
        self.fps = fps

        if self.type == "webcam":
            self.camera = cv2.VideoCapture(0)
            self.webcam_capture_thread = threading.Thread(
                target=capture_webcam_frames,
                daemon=True,
                args=(
                    self.camera,
                    self.stop_camera_event,
                    self.display_queue,
                    self.save_queue,
                    self.record_event,
                    self.fps,
                ),
            )
            self.webcam_capture_thread.start()
        else:
            self.camera = pylon.InstantCamera(
                pylon.TlFactory.GetInstance().CreateFirstDevice()
            )
            self.camera.Open()
            settings_file = 'Color_Yunhao/color_Yunhao/calibs/features_used_for_positive_picture.pfs'
            if settings_file:
                pylon.FeaturePersistence.Load(settings_file, self.camera.GetNodeMap(), True)
            # Set the upper limit of the camera's frame rate to 30 fps
            self.camera.AcquisitionFrameRateEnable.SetValue(True)
            self.camera.AcquisitionFrameRate.SetValue(self.fps)
            self.camera.PixelFormat = 'RGB8'
            # self.camera.ExposureAuto.SetValue("Off")
            # self.camera.ExposureTime.SetValue(1000)
            self.camera.RegisterImageEventHandler(
                ImageSaverHandler(
                    self.save_queue, self.display_queue, self.record_event
                ),
                pylon.RegistrationMode_ReplaceAll,
                pylon.Cleanup_Delete,
            )
            self.camera.StartGrabbing(
                pylon.GrabStrategy_OneByOne, pylon.GrabLoop_ProvidedByInstantCamera
            )

    def get_latest_frame(self, width):
        try:
            raw_image, timestamp = self.display_queue.get(timeout=0.1)
            image = Image.fromarray(raw_image).convert('RGB')  # Convert directly to RGB
            
            img = image.resize(
                (width, int(width * image.height / image.width))
        )
            tk_img = ImageTk.PhotoImage(image=img)
            return tk_img, timestamp
        except queue.Empty:
            return None, ""

    def start_recording(self, folder):
        self.record_event.set()
        self.saver_thread = threading.Thread(
            target=save_image_async,
            args=(folder, self.record_event, self.save_queue),
        )
        self.saver_thread.start()

    def stop_recording(self):
        self.record_event.clear()

    def release(self):
        self.stop_recording()
        self.stop_camera_event.set()
        if self.type == "webcam":
            self.camera.release()
            if self.webcam_capture_thread.is_alive():
                self.webcam_capture_thread.join()
        else:
            self.camera.StopGrabbing()
            self.camera.Close()

        if self.saver_thread is not None and self.saver_thread.is_alive():
            self.saver_thread.join()
