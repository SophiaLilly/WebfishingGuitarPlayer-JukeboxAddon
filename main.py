# Get the position of the mouse cursor when the left mouse button is clicked without a GUI.
# and print it to the console.

import pyautogui
import time
import win32gui
import random
import cv2
import pytesseract
from tkinter import *
import threading

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


def run_guitar_player():
    win32gui.EnumWindows(guitar_player.jukebox, None)


class GuitarPlayer:

    def __init__(self):
        self.bounds = None
        self.song_bounds = None
        self.text = None
        self.minutes = None
        self.seconds = None
        self.img = None
        self.root = None
        self.hwnd = None
        self.stop_song = False

        self.t1 = threading.Thread(target=run_guitar_player)
        self.t2 = threading.Thread(target=self.jukebox_window)
        self.t3 = threading.Thread(target=self.detect_window_movement)

    def main(self):
        print('Starting Jukebox')
        if not self.t1.is_alive():
            print('Jukebox thread started')
            self.t1 = threading.Thread(target=run_guitar_player)
            self.t1.start()

        if not self.t2.is_alive():
            print('Jukebox window thread started')
            self.t2.start()

        if not self.t3.is_alive():
            print('Detect window movement thread started')
            self.t3.start()

        self.t1.join()

    def jukebox_window(self):
        # Create a Tkinter window and attach it to the Guitar Player window

        self.root = Tk()
        self.root.title('Jukebox')
        self.root.geometry('200x200')
        self.root.resizable(False, False)

        Label(self.root, text='Guitar Player Jukebox').pack()
        self.root.overrideredirect(True)
        # Find the Guitar Player window and attach the Tkinter window to it
        self.join_window()

        Button(self.root, text='Skip Song', command=self.kill_song).pack()

        self.root.mainloop()

    def kill_song(self):
        self.stop_song = True

    def join_window(self):
        if win32gui.IsWindowVisible(self.hwnd) and 'Guitar Player' in win32gui.GetWindowText(self.hwnd):
            #print(win32gui.GetWindowRect(self.hwnd))
            self.root.geometry('+{}+{}'.format(win32gui.GetWindowRect(self.hwnd)[0] - 200,
                                               win32gui.GetWindowRect(self.hwnd)[1]))

    def jukebox(self, hwnd, top_windows):
        self.hwnd = hwnd
        if win32gui.IsWindowVisible(hwnd) and 'Guitar Player' in win32gui.GetWindowText(hwnd):
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)

            self.bounds = x, y, x2, y2 = win32gui.GetWindowRect(hwnd)
            self.song_bounds = (x + 40, y + 90, x2 - 40, y2 - 200)

            self.get_random_song()
            self.click_play()
            self.save_image()

            if self.scan_image(cv2.INTER_CUBIC) != '' and self.text[0].isdigit() and self.text[2:4].isdigit():
                self.no_errors()
                return
            print('First Scan Failed')

            if self.scan_image(cv2.INTER_LINEAR) != '' and self.text[0].isdigit() and self.text[2:4].isdigit():
                self.no_errors()
                return
            print('Second Scan Failed')

            if self.scan_image(cv2.INTER_AREA) != '' and self.text[0].isdigit() and self.text[2:4].isdigit():
                self.no_errors()
                return
            print('Third Scan Failed')

            if self.scan_image(cv2.INTER_LANCZOS4) != '' and self.text[0].isdigit() and self.text[2:4].isdigit():
                self.no_errors()
                return
            print('Fourth Scan Failed')

            if self.scan_image(cv2.ADAPTIVE_THRESH_GAUSSIAN_C) != '' and self.text[0].isdigit() and self.text[
                                                                                                    2:4].isdigit():
                self.no_errors()
                return
            print('Fifth Scan Failed')

            if self.scan_image(cv2.INTER_NEAREST) != '' and self.text[0].isdigit() and self.text[2:4].isdigit():
                self.no_errors()
                return
            print('All scans failed, we are cooked brothers.')

            self.click_stop()

    def detect_window_movement(self):
        pass
        # Detect if the window has moved and update the bounds
        while True:
            if self.bounds != win32gui.GetWindowRect(self.hwnd):
                self.bounds = x, y, x2, y2 = win32gui.GetWindowRect(self.hwnd)
                self.song_bounds = (x + 40, y + 90, x2 - 40, y2 - 200)
                self.join_window()

    def get_random_song(self):
        time.sleep(0.1)
        pyautogui.moveTo(x=random.randint(self.song_bounds[0], self.song_bounds[2]),
                         y=random.randint(self.song_bounds[1], self.song_bounds[3]))
        # Scroll the mouse wheel a bit either up or down
        pyautogui.scroll(random.randint(-3, 3))

        time.sleep(0.1)
        pyautogui.click()

    def click_play(self):
        time.sleep(0.1)
        pyautogui.moveTo(self.bounds[0] + 50, self.bounds[1] + 425)
        pyautogui.click()

    def click_stop(self, after_seconds=0.1):
        time.sleep(after_seconds)
        pyautogui.moveTo(self.bounds[0] + 250, self.bounds[1] + 425)
        pyautogui.click()

    def save_image(self):
        time.sleep(0.1)
        im = pyautogui.screenshot(region=(self.bounds[0] + 152, self.bounds[1] + 375, 30, 17))
        im.save('screenshot.png')

    def scan_image(self, interpolation_method):
        self.img = cv2.imread('screenshot.png')
        self.img = cv2.resize(self.img, None, fx=8, fy=8, interpolation=interpolation_method)
        self.text = pytesseract.image_to_string(self.img)
        return self.text

    def no_errors(self):
        print('No errors')
        time.sleep(0.1)
        minutes = int(self.text[0])
        seconds = int(self.text[2:4])
        print(minutes * 60 + seconds)

        # Wait for the Guitar Player to finish playing the song
        # time.sleep(minutes * 60 + seconds)
        # Sleep 1 second at a time until the song is finished so that it can be stopped
        for i in range(minutes * 60 + seconds):
            print(i)
            time.sleep(1)
            if self.stop_song:
                self.stop_song = False
                break

        print('Song is finished')
        self.click_stop(1)


guitar_player = GuitarPlayer()





# guitar_player.main()
while True:
    # win32gui.EnumWindows(guitar_player.jukebox, None)
    # guitar_player.jukebox_window()
    guitar_player.main()
    # Create a new thread for the Jukebox, if the Jukebox is already running, nothing will happen
    # If the thread finishes, it will be restarted
    # t = threading.Thread(target=run_guitar_player)
    # t.start()
    # t1 = threading.Thread(target=run_guitar_player)
    # if not t1.is_alive():
    # t1.start()

    # Create a new thread for the Jukebox window
    # t2 = threading.Thread(target=guitar_player.jukebox_window)
    # if not t2.is_alive():
    # t2.start()

    # Create a new thread for detecting window movement
    # t3 = threading.Thread(target=guitar_player.detect_window_movement)
    # if not t3.is_alive():
    # t3.start()

    # t1.join()
    # t2.join()
    # t3.join()
