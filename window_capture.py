# import cv2
import numpy as np
from ctypes import windll
import win32gui
import win32ui


class WindowCapture:

    # Atributos
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # Constuctor
    def __init__(self, window_name=None):

        windll.user32.SetProcessDPIAware()
        # Nome da Janela que vai tirar screenshot
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception(f"Window not found: {window_name}")

        # Width and Height da tela que deseja tirar screenshot
        window_rect = win32gui.GetClientRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]
        # self.w = 1280
        # self.h = 800

        # # Remover a titlebar e black borders da janela
        # border_pixels = 8
        # titlebar_pixels = 30
        # self.w = self.w - (border_pixels * 2)
        # self.h = self.h - titlebar_pixels - border_pixels
        # self.cropped_x = border_pixels
        # self.cropped_y = titlebar_pixels

        # # set the cropped coordinates offset so we can translate screeshot
        # # images into actual screen positions
        # # Ao remover black borders da tela, perdemos a precisão das coordenadas. Por isso é necessário fazer o ajuste.
        # self.offset_x = window_rect[0] + self.cropped_x
        # self.offset_y = window_rect[1] + self.cropped_y


    def get_screenshot(self):

        # Adapted from https://stackoverflow.com/questions/19695214/screenshot-of-inactive-window-printwindow-win32gui

        hwnd_dc = win32gui.GetWindowDC(self.hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, self.w, self.h)
        save_dc.SelectObject(bitmap)

        # If Special K is running, this number is 3. If not, 1
        result = windll.user32.PrintWindow(self.hwnd, save_dc.GetSafeHdc(), 3)

        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)

        # img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
        img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
        img = np.ascontiguousarray(img)[..., :-1]  # make image C_CONTIGUOUS and drop alpha channel

        
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwnd_dc)

        return img
    
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)
    
    # Traduz a posição de um pixel em uma screenshot para o pixel de uma posição na tela.
    # pos = (x, y)
    # Warning: Se você mover a tela que está sendo capturada após a execução ser startada
    # vai fazer que o método retorne as coordenadas incorretas, pois a posiçãio da tela só é calculada no construtor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)