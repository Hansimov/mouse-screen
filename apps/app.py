import cv2
import numpy as np

from mss import mss
from pynput import mouse
from tclogger import logger


class MainApp:
    def __init__(self):
        self.window_name = "Mouse-Screen"
        self.ratio = 1.5
        self.window_width = int(1920 / self.ratio)
        self.window_height = int(1080 / self.ratio)
        self.mouse_x, self.mouse_y = 0, 0
        self.get_monitor_bounds()
        self.setup_window()

    def setup_window(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.window_width, self.window_height)

    def on_mouse_move(self, x, y):
        self.mouse_x, self.mouse_y = x, y

    def detect_active_monitor(self):
        """detect active monitor, where the mouse is currently located"""
        self.active_monitor = None
        for idx, monitor in enumerate(self.monitors[1:]):
            if (
                self.mouse_x >= monitor["left"]
                and self.mouse_x <= monitor["left"] + monitor["width"]
                and self.mouse_y >= monitor["top"]
                and self.mouse_y <= monitor["top"] + monitor["height"]
            ):
                self.active_monitor = monitor
                break
        if self.active_monitor is None:
            self.active_monitor = self.monitors[0]

    def get_monitor_bounds(self):
        """get the bounds of all monitors"""
        self.monitor_top_bound = 0
        self.monitor_left_bound = 0
        self.monitor_bottom_bound = 0
        self.monitor_right_bound = 0

        with mss() as sct:
            combined_monitor = sct.monitors[0]
            self.monitor_left_bound = combined_monitor["left"]
            self.monitor_right_bound = (
                combined_monitor["left"] + combined_monitor["width"]
            )
            self.monitor_top_bound = combined_monitor["top"]
            self.monitor_bottom_bound = (
                combined_monitor["top"] + combined_monitor["height"]
            )

    def calc_mouse_region(self):
        """calculate the region of the screen to capture based on the mouse position"""
        self.region_x1 = min(
            max(
                self.mouse_x - self.window_width // 2,
                self.monitor_left_bound,
            ),
            self.monitor_right_bound - self.window_width,
        )
        self.region_y1 = min(
            max(
                self.mouse_y - self.window_height // 2,
                self.monitor_top_bound,
            ),
            self.monitor_bottom_bound - self.window_height,
        )

        self.mouse_region = {
            "top": self.region_y1,
            "left": self.region_x1,
            "width": self.window_width,
            "height": self.window_height,
        }

    def run(self):
        """use mss to capture screen, and use cv2 to real-time display each frame"""
        with mss() as sct:
            self.monitors = sct.monitors
            with mouse.Listener(on_move=self.on_mouse_move) as listener:
                while True:
                    self.detect_active_monitor()
                    self.calc_mouse_region()
                    frame = sct.grab(self.mouse_region)
                    frame_np = np.array(frame)
                    cv2.imshow(self.window_name, frame_np)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        cv2.destroyAllWindows()
                        break


if __name__ == "__main__":
    app = MainApp()
    app.run()

    # python -m apps.app
