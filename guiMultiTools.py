import threading
import multiprocessing
from tkinter import *
from PIL import Image, ImageTk
import time
import os

class WindowController:
    def __init__(self):
        self.root = None
        self.manager = multiprocessing.Manager()
        self.sap = SapRobot()
        self.event_init = threading.Event()

    def run_gui(self):
        self.root = Window(self, 300 ,300)
        self.root.myloop()


    def change_image(self, i):
        if self.root is not None:
            self.root.current['image'] = f'frame{i}'

    def anim_loop(self):
        self.event_init.wait()

        while self.root.run:
            i = 0
            while self.root.status['sap']:
                self.change_image(i)
                i += 1
                if i == 12:
                    i = 0
                time.sleep(0.25)
            time.sleep(0.2)

    def test_show(self):
        if self.root is not None:
            print(self.root.current['image'])

    def run_sap(self):
        self.p1 = multiprocessing.Process(target=self.sap.to_sap, args=[self.root.current, self.root.status])
        self.p1.start()

# class LabelText:
#     def __init__(self, text):
#         self.text = text
    
#     def change_text(self, new_text):
#         self.text = new_text

class SapRobot:
    def to_sap(self, currents, status):
        status['sap'] = True
        for i in range(10):
            currents['text'] = f'Running sap... {i}'
            time.sleep(0.75)
        currents['text'] = 'SAP done'
        status['sap'] = False
        currents['image'] = None

class Window(Tk):
    def __init__(self, control, width, height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry(f'{width}x{height}')
        self.c = control
        self.run = True
        self.load_imgs()

        self.status = self.c.manager.dict()
        self.current = self.c.manager.dict()
        self.status['sap'] = False
        self.current['text'] = 'nic'
        self.current['image'] = None
        # self.current_image = self.c.manager.Value('i', '') #''#self.images['anim']['frame0']
        # self.current_text = self.c.manager.Value('i', 'nic')

        self.make_widgs()

    def make_widgs(self):
        self.buttons = {}
        self.labels = {}

        self.labels['image'] = Label(self)
        self.labels['image'].pack()

        self.labels['message'] = Label(self, text=self.current['text'])
        self.labels['message'].pack()

        self.buttons['run'] = Button(self, text='Run', command=self.c.run_sap)
        self.buttons['run'].pack()

        self.buttons['quit'] = Button(self, text='Quit', command=self._exit_app)
        self.buttons['quit'].pack()

    def load_imgs(self):
        self.images = {}
        self.images['anim'] = {}
        for i in range(len(os.listdir('./loading'))):
            im = Image.open(f'loading/f{i}.png')
            self.images['anim'][f'frame{i}'] = ImageTk.PhotoImage(im)

    def _exit_app(self):
        self.run = False

    def myloop(self):
        self.c.event_init.set()
        while self.run:
            # if str(self.labels['image']['image']) != str(self.current['image']):
            if self.current['image'] is not None:
                self.labels['image']['image'] = self.images['anim'][self.current['image']]
            else:
                self.labels['image']['image'] = ''
            if self.labels['message']['text'] != self.current['text']:
                self.labels['message']['text'] = self.current['text']
            self.update()

def main():
    c = WindowController()

    t1 = threading.Thread(target=c.run_gui)
    t1.start()

    t2 = threading.Thread(target=c.anim_loop, daemon=True)
    t2.start()

    # c.run_gui()

    k = 0

    c.event_init.wait()
    while c.root.run:
        print(f'Im still working on main thread... {k}')
        if k+1 == 20:
            k = 0
        else:
            k += 1
        time.sleep(0.5)


if __name__ == '__main__':
    main()