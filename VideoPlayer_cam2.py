from tkinter import*
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import numpy as np
import cv2
import os
import copy
import time
import pcn
import io
import PySimpleGUI as sg
from PIL import Image, ImageColor, ImageDraw



class VideoPlayer2(ttk.Frame):

    def __init__(self, parent: ttk.Frame=None, **prop: dict): 

        setup = self.set_setup(prop)

        ttk.Frame.__init__(self, parent)

        # private
        self.__cap = object
        self.__size = (640, 480)
        self.__image_ratio = 480/640
        self.__frames_numbers = 0
        self.__play = False
        self.__algo = False
        self.__frame = np.array
        self.__initialdir = "/"
        self.__initialdir_movie = "/"

        # protected
        self._command = []

        # public
        self.frame = np.array
        # build widget
        self._build_widget(parent, setup)
        self.play_movie()


    @property
    def frame(self)->np.array:
        return self.__frame

    @property
    def command(self):
        return self.__command

    @property
    def algo(self)->bool:
        return self.__algo

    @frame.setter
    def frame(self, frame: np.array):
        self.__frame = frame

        if self.algo and callable(self._command):
            # convert image to numpy image
            matrix_image = np.array(self.frame)
            self._command(matrix_image)

    @command.setter
    def command(self, command):
        # check if the command is lambda expression
        if callable(command):
            self._command = command


    @algo.setter
    def algo(self, algo: bool):
        if isinstance(algo, bool):
            self.__algo = algo

    def set_setup(self, prop: dict)->dict:
        default = {'play':  True, 'camera': False, 'pause': True, 'stop': True, 'image': False, 'algo': False}
        setup = default.copy()
        setup.update(prop)
        self.algo = setup['algo']
        return setup


    def _build_widget(self, parent: ttk.Frame=None, setup: dict=dict):

        if parent is None:
            self.master.title("Камера 3")
            self.master.geometry("900x500+0+0")
            self.main_panel = Frame(self.master, relief=SUNKEN)
            self.main_panel.place(relx=0, rely=0, relwidth=1, relheight=1)
        else:
            self.main_panel = parent

        # main panel
        self.main_panel.config(bg="black")

        icon_width = 45
        icon_height = 50
        canvas_progressbar_height = 2
        # frame_height = int(self.main_panel.cget('height')/10-icon_height-canvas_progressbar_height)

        self.canvas_image = Canvas(self.main_panel, bg="black", highlightthickness=0)
        self.canvas_image.pack(fill=BOTH, expand=True, side=TOP)
        self.canvas_image.bind("<Configure>", self.resize)

        self.board = Label(self.canvas_image, bg="black", width=44, height=14)
        self.board.pack(fill=BOTH, pady=10, expand=True)
        
  

    def extract(self):
        if self.algo:

            self.algo = False
            self.button_run_algo.config(text="Run algo")
        else:
            self.algo = True
            self.button_run_algo.config(text="Stop algo")

    def resize(self, event):
        w, h = event.width, event.height

        width = h/self.__image_ratio
        height = h

        if width > w:
            width = w
            height = w*self.__image_ratio

        self.__size = (int(width), int(height))
        if Image.isImageType(self.frame):
            image = copy.deepcopy(self.frame)
            self.show_image(image)


    def show_image(self, image):

        width =  self.master.winfo_width() # Ширина окна
        height =  self.master.winfo_height() # Высота окна
        image = image.resize((int(width*0.91), int(height*0.96))) # Изменяем размер картинки
        self.photo = ImageTk.PhotoImage(image) # Создаём PhotoImage
        self.board.config(image=self.photo)
        self.board.image = self.photo

        self.board.update()


    def play_movie(self):

        self.__cap = cv2.VideoCapture("D:\\Dataset_for bus\\4\\cam3.mp4")
        self.__frames_numbers = int(self.__cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.__image_ratio = self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.__play = True    
        self.run_frames()



    def run_frames(self):
        frame_pass = 0
        #occurences = {}

        while self.__cap.isOpened():
            time.sleep(0.05)
            if self.__play:
                # update the frame number
                ret, image_matrix = self.__cap.read()
                winlist = pcn.detect(image_matrix)
                faces = len(pcn.crop(image_matrix, winlist))
                         
                #self.face_counter.configure(text=str(faces) + " passengers detected")
                image_matrix = pcn.draw(image_matrix, winlist)
                # self.frame = image_matrix
                if ret:
                    frame_pass += 1
                    self.update_progress(frame_pass)

                    # convert matrix image to pillow image object
                    self.frame = self.matrix_to_pillow(image_matrix)
                    self.show_image(self.frame)

                # refresh image display
            self.board.update()                     
        self.__cap.release()
        cv2.destroyAllWindows()


    @staticmethod
    def matrix_to_pillow(frame: np.array):
        # convert to BGR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # convert matrix image to pillow image object
        frame_pillow = Image.fromarray(frame_bgr)
        return frame_pillow

    def update_progress(self, frame_pass: int=0, frames_numbers: int = None):
        if frames_numbers is None:
            frames_numbers = self.__frames_numbers


def extract_image(matrix_image: np.array):
    # apply algo
    resize_image = cv2.resize(matrix_image, dsize=(640, 480), interpolation=cv2.INTER_CUBIC)
    cv2.imshow('frame', resize_image)


def RunApp():
    vid = VideoPlayer2(image=True, play=True, camera=True, algo=True)
    #vid.command = lambda frame: extract_image(frame)
    #vid.mainloop()
