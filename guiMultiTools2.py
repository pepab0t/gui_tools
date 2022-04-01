import threading
import multiprocessing
from tkinter import *
from PIL import Image, ImageTk
import time
import os
from abc import ABC, abstractmethod


class Gui(ABC, Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.buttons = {}
        self.labels = {}
        self.entries = {}
        self.frames = {}

    @abstractmethod
    def make_widgs(self):
        '''function that creates widgets'''

    @abstractmethod
    def update_loop(self):
        '''updating widgets, loop with tk.after function'''

    @staticmethod
    def load_imgs(source: list[dict]) -> dict:
        images = {}

        for d in source:
            images[d['key']] = []
            if os.path.isdir(d['path']):
                for im in os.listdir(d['path']):
                    im = Image.open(d['path']+ '/' + im)
                    images[d['key']].append(ImageTk.PhotoImage(im))                
            else:
                im = Image.open(d['path'])
                images[d['key']].append(ImageTk.PhotoImage(im))                

        return images

    def make_anims(self, images: list[str], label_names: list[str]):
        '''This function creates dict of LoadingAnimation objects with list of images to animate and appropriate label'''
        anim = {}

        for img, lab in zip(images, label_names):
            if img in self.images:
                anim[lab] = LoadingAnimation(self.images[img], self.labels[lab])

        return anim

class WindowController:
    def __init__(self, sap_obj):
        self.sap = sap_obj

        self.manager = multiprocessing.Manager()
        self.event_init = threading.Event()

        self.processes  = {}

        self.status = self.manager.dict()
        self.status['sap'] = False
        self.status['dummy'] = False

        self.texts = self.manager.dict()

    def run_gui(self, width, height, GuiClass: Gui, source: list[dict], *args, **kwargs):
        self.root = GuiClass(width ,height, self, source, *args, **kwargs)
        self.root.mainloop()

    def run_sap(self, proc_name: str):
        if proc_name not in self.status.keys():
            raise Exception('proc_name is not in status.keys()')
        args = [self.texts, str(self.root.vars['message1']), self.status, proc_name]
        self.processes[proc_name] = multiprocessing.Process(target=self.sap.to_sap, args=args)
        self.processes[proc_name].start()

    def run_dummy(self, proc_name):
        if proc_name not in self.status.keys():
            raise Exception(f'proc_name: {proc_name} is not in status.keys()')
        args = [self.texts, str(self.root.vars['message2']), self.status, proc_name]
        self.processes[proc_name] = multiprocessing.Process(target=self.sap.dummy_func, args=args)
        self.processes[proc_name].start()


class SapRobot:
    def to_sap(self, d, textvar: str, status: dict, process_key: str):
        status[process_key] = True
        for i in range(10):
            d[textvar] = f'Running sap... {i}'
            time.sleep(0.75)
        d[textvar] = 'SAP done'
        status[process_key] = False

    def dummy_func(self, d, textvar: str, status: dict, process_key: str):
        status[process_key] = True
        for i in range(10, 0, -1):
            d[textvar] = f"Runnin another process.. {i}"
            time.sleep(1)
        d[textvar] = f"COMPLETED! "
        status[process_key] = False

class LoadingAnimation:
    def __init__(self, images: list[ImageTk.PhotoImage], label: Label, default_image=''):
        '''images should be list with image object of all animation frames'''

        self._active = False
    
        self.images = images
        self.current_img = 0
        self.my_label = label
        self.def_img = default_image
    
    def set_default_image(self, image: ImageTk.PhotoImage):
        self.def_img = image

    def start(self):
        self._active = True
        print('started')

    def stop(self):
        self._active = False
        self.reset()
        self.my_label['image'] = self.def_img

    def tick(self):
        self.my_label['image'] = self.images[self.current_img]
        self.current_img += 1
        if self.current_img == len(self.images):
            self.current_img = 0
        
    def reset(self):
        self.current_img = 0

    @property
    def Active(self):
        return self._active

    def __repr__(self):
        out = f'status: {self._active}, current_img: {self.images[self.current_img]}'
        return out

class Window(Gui):
    def __init__(self, width: int, height: int, control: WindowController, source: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry(f'{width}x{height}')

        self.c = control

        self.images = self.load_imgs(source)

        self.make_widgs()

        self.anim = self.make_anims(images=['anim2', 'anim2'], label_names=['image', 'image2'])

        self.updating = self.update_loop()
        self.animating = self.anim_loop()

    def make_widgs(self):
        self.vars = {}

        self.labels['image'] = Label(self)
        self.labels['image'].pack()

        self.vars['message1'] = StringVar()
        self.labels['message1'] = Label(self, textvariable=self.vars['message1'])
        self.labels['message1'].pack()

        self.buttons['run1'] = Button(self, text='Run sap', command=lambda: self.c.run_sap('sap'))
        self.buttons['run1'].pack()

        self.labels['image2'] = Label(self)
        self.labels['image2'].pack()

        self.vars['message2'] = StringVar()
        self.labels['message2'] = Label(self, textvariable=self.vars['message2'])
        self.labels['message2'].pack()

        self.buttons['run2'] = Button(self, text='Run another process', command=lambda: self.c.run_dummy('dummy'))
        self.buttons['run2'].pack()

        self.buttons['quit'] = Button(self, text='Quit', command=self._exit_app)
        self.buttons['quit'].pack(pady=10)

        for v in self.vars.values():
            self.c.texts[str(v)] = None

        # self.texts = self.c.manager.dict()

    def _exit_app(self):
        for proc in self.c.processes.values():
            if proc is not None:
                proc.terminate()

        self.destroy()

    def update_text(self, **variables):
        for v in variables.values():
            val = self.c.texts[str(v)]
            if val is not None:
                v.set(str(val))

    def anim_loop(self):
        for v in self.anim.values():
            if v.Active:
                v.tick()

        self.after(100, self.anim_loop)

    def handle_loading_animations(self, *pair: tuple):
        '''Pair is self.c.status[] and appropriate animation tuple'''
        for status, animation in pair:
            if status and not animation.Active:
                animation.start()
            elif not status and animation.Active:
                animation.stop()
                animation.reset()

    def update_loop(self):
        self.handle_loading_animations( (self.c.status['sap'], self.anim['image']), (self.c.status['dummy'], self.anim['image2']) )
        self.update_text(**self.vars)

        ### run again
        self.after(50, self.update_loop)
        

def main(width, height):
    source = [
        {
            'key': 'anim1',
            'path': 'loading/loading_one/'
        },
        {
            'key': 'anim2',
            'path': 'loading/loading_two/'
        }
    ]

    sap = SapRobot()

    w = WindowController(sap)

    w.run_gui(width, height, Window, source)



if __name__ == '__main__':
    multiprocessing.freeze_support()

    main(400, 400)