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
import VideoPlayer_cam2


class VideoPlayer(ttk.Frame):

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
        
        self.startX = 15312
        self.startY = 32473
        self.startSpeed = 30
        
        self.curX = self.startX
        self.curY = self.startY
        self.curS = self.startSpeed

        # protected
        self._command = []

        # public
        self.frame = np.array
        # build widget
        self._build_widget(parent, setup)

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
            self.master.title("Детектирование пассажиров")
            self.master.geometry("1200x700+0+0")
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

        canvas_progressbar = Canvas(self.main_panel, relief=FLAT, height=canvas_progressbar_height, 
                                    bg="black", highlightthickness=0)
        canvas_progressbar.pack(fill=X, padx=10, pady=3)

        s = ttk.Style()
        s.theme_use('clam')
        s.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue', thickness=1)
        self.progressbar = ttk.Progressbar(canvas_progressbar, style="blue.Horizontal.TProgressbar", orient='horizontal',
                                           length=200, mode="determinate")

        self.progressbar.pack(fill=X, padx=10, pady=0, expand=True)

        # control panel
        control_frame = Frame(self.main_panel, bg="black", relief=SUNKEN)
        control_frame.pack(side=BOTTOM, fill=X, padx=20)

        icons_path = os.path.abspath(os.path.join(os.curdir, 'Icons'))
        

        
        
        if setup['play']:
            # play video button button_live_video
            self.icon_load = PhotoImage(file=os.path.join(icons_path, 'load2.PNG'))
            self.icon_play = PhotoImage(file=os.path.join(icons_path, 'play2.PNG'))
            button_live_video = Button(control_frame, padx=10, pady=15, bd=4, fg="white", font=('arial', 12, 'bold'),
                                       text="> Load Video", bg='black', image=self.icon_load, height=icon_height,
                                       width=icon_width, command=lambda: self.load_movie())
            button_live_video.pack(side='left')



        if setup['pause']:
            # pause video button button_live_video
            self.icon_pause = PhotoImage(file=os.path.join(icons_path, 'pause2.PNG'))

            self.button_pause_video = Button(control_frame, padx=10, pady=15, bd=4, fg="white",
                                             font=('arial', 12, 'bold'),
                                             text="Pause", bg='black', image=self.icon_pause,
                                             height=icon_height, width=icon_width,
                                             command=lambda: self.pause_movie())
            self.button_pause_video.pack(side='left')

        if setup['stop']:
            # stop video button button_live_video
            self.icon_stop = PhotoImage(file=os.path.join(icons_path, 'stop2.PNG'))
            button_stop_video = Button(control_frame, padx=10, pady=15, bd=4, fg="white", font=('arial', 12, 'bold'),
                                       text="stop", bg='black', height=icon_height, width=icon_width,
                                       image=self.icon_stop,
                                       command=lambda: self.stop_movie())
            button_stop_video.pack(side='left')

        # edit box
        self.frame_counter = Label(control_frame, height=2, width=15, padx=20, pady=15, bd=4,
                                   bg='black', fg="gray", font=('arial', 10, 'bold'))
        self.frame_counter.pack(side='left')
        
        
        self.face_counter = Label(control_frame, height=2, width=15, padx=20, pady=15, bd=4,
                                   bg='black', fg="gray", font=('arial', 10, 'bold'))
        self.face_counter.pack(side='left')
        
        self.coordX = Label(control_frame, height=2, width=15, padx=20, pady=15, bd=2,
                                   bg='black', fg="gray", font=('arial', 10, 'bold'))
        self.coordX.pack(side='left')
        
        self.coordY = Label(control_frame, height=2, width=15, padx=10, pady=15, bd=2,
                                   bg='black', fg="gray", font=('arial', 10, 'bold'))
        self.coordY.pack(side='left')
        
        self.speed = Label(control_frame, height=2, width=15, padx=10, pady=15, bd=4,
                                   bg='black', fg="gray", font=('arial', 10, 'bold'))
        self.speed.pack(side='left')
        
        self.stopResult = Label(control_frame, height=2, width=15, padx=10, pady=15, bd=4,
                                   bg='black', fg="red", font=('arial', 15, 'bold'))
        self.stopResult.pack(side='left')
        
        

    
    def GenerateInfos(self, framesCount, stopArray):
      info = []
      for i in range(framesCount):
        info.append(self.startSpeed)
      for i in stopArray:
        left = i
        if(left>=5):
          for j in range(5):
            left = left - 1
            if(info[left] == self.startSpeed):
              info[left] = (j+1)/5*self.startSpeed
        else:
          divide = left
          for j in range(left):
            left = left - 1
            if(info[left] == self.startSpeed):
              info[left] = (j+1)/divide*self.startSpeed 
        
        right = i
        if(right<(framesCount-5)):
          for j in range(5):
            right = right + 1
            if(info[right] == self.startSpeed):
              info[right] = (j+1)/5*self.startSpeed
        else:
          divide = framesCount-right
          for j in range(divide-1):
            right = right + 1
            if(info[right] == self.startSpeed):
              info[right] = (j+1)/divide*self.startSpeed 
    
        for i in stopArray:
          info[i] = 0
    
        x = self.curX
        y = self.curY
        allInfo = []
        for i in info:
          if(i!=0):
            x = x - 1
            y = y + 1
          allInfo.append((x,y,i))
      return allInfo
  

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

        # resize image
        #image.thumbnail(self.__size)
        #
        #self.photo = ImageTk.PhotoImage(image=image)
        # The Label widget is a standard Tkinter widget used to display a text or image on the screen.
        #self.board.config(image=self.photo)
        #self.board.image = self.photo

        width =  self.master.winfo_width() # Ширина окна
        height =  self.master.winfo_height() # Высота окна
        image = image.resize((int(width*0.91), int(height*0.96))) # Изменяем размер картинки
        self.photo = ImageTk.PhotoImage(image) # Создаём PhotoImage
        self.board.config(image=self.photo)
        self.board.image = self.photo
        
        # refresh image display
        self.board.update()


    def load_movie(self):
        
        movie_filename = filedialog.askopenfilename(initialdir=self.__initialdir_movie,
                                                    title="Select the movie to play",
                                                    filetypes=(("MP4 files", "*.MP4"),
                                                               ("AVI files", "*.AVI"),
                                                               ("all files", "*.*")))
        if len(movie_filename) != 0:
            self.__initialdir_movie = os.path.dirname(os.path.abspath(movie_filename))
            VideoPlayer_cam2.RunApp()
            self.play_movie(movie_filename)

        pass


    def play_movie(self, movie_filename: str):

        self.__cap = cv2.VideoCapture(movie_filename)
        self.__frames_numbers = int(self.__cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.__image_ratio = self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH)

        self.progressbar["maximum"] = self.__frames_numbers
        self.__play = True

        self.run_frames()



    def run_frames(self):
        frame_pass = 0
        #occurences = {}
        
        dictInfos = {}    
        info1 = []
        for i in range(self.__frames_numbers):
          if (i>=45):
            info1.append(i)      
        dictInfos["cam2.mp4"] = self.GenerateInfos(self.__frames_numbers, info1)

        while self.__cap.isOpened():
            time.sleep(0.05)
            if self.__play:
                # update the frame number
                ret, image_matrix = self.__cap.read()
                winlist = pcn.detect(image_matrix)
                faces = len(pcn.crop(image_matrix, winlist))
                self.face_counter.configure(text=str(faces) + " passengers detected")
                self.coordX.configure(text="Coord X:"+str(dictInfos["cam2.mp4"][frame_pass][0]))
                self.coordY.configure(text="Coord Y:"+str(dictInfos["cam2.mp4"][frame_pass][1]))
                
                speed = dictInfos["cam2.mp4"][frame_pass][2]
                self.speed.configure(text="Speed:"+str(speed))
                
                if(speed == 0):
                    isStop = "Bus stop!"
                else:
                    isStop = ""
                self.stopResult.configure(text=isStop) 


                 
                '''
                if (faces in occurences):
                    occurences[faces] = occurences[faces] + 1
                else:
                    occurences[faces] = 1
               
                if(frame_pass%5==0):
                        max_value = 0
                        result_faces = 0
                        for key in occurences.keys():
                          if(occurences[key] > max_value):
                            max_value = occurences[key]
                            result_faces = key
                        self.face_counter.configure(text=str(result_faces) + " passengers detected")
                        occurences.clear()
                ''' 
                         
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

    def stop_movie(self):

        self.pause_movie()
        self.__cap.release()

        cv2.destroyAllWindows()
        self.update_progress(0, 0)

    def pause_movie(self):

        if self.__cap.isOpened():
            self.__play = not self.__play

        else:
            self.__play = False

        if self.__play:
            self.button_pause_video.config(image=self.icon_pause)
        elif not self.__play:
            self.button_pause_video.config(image=self.icon_play)

    def update_progress(self, frame_pass: int=0, frames_numbers: int = None):

        if frames_numbers is None:
            frames_numbers = self.__frames_numbers

        self.frame_counter.configure(text=str(frame_pass) + " / " + str(frames_numbers))
        # update the progressbar
        self.progressbar["value"] = frame_pass
        self.progressbar.update()
        
    



def main():
    vid = VideoPlayer(image=True, play=True, camera=True, algo=True)
    vid.command = lambda frame: extract_image(frame)
    vid.mainloop()


def extract_image(matrix_image: np.array):

    # apply algo
    resize_image = cv2.resize(matrix_image, dsize=(640, 480), interpolation=cv2.INTER_CUBIC)
    cv2.imshow('frame', resize_image)


if __name__ == "__main__":
    main()
