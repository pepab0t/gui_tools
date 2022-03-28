import threading
import multiprocessing
from tkinter import *
from PIL import Image, ImageTk
import time
import os

def dummy_func(current, status):
    status['proc2'] = True
    for i in range(10, 0, -1):
        current['message2'] = f"Runnin another process.. {i}"
        time.sleep(1)
    current['message2'] = f"COMPLETED! "
    status['proc2'] = False
    current['image2'] = None

class WindowController:
    def __init__(self):
        self.root = None
        self.manager = multiprocessing.Manager()
        self.sap = SapRobot()
        self.event_init = threading.Event()

        self.processes  = {}

    def run_gui(self, width, height):
        self.root = Window(self, width ,height)
        self.root.myloop()


    def change_image(self, i, label_key):
        if self.root is not None:
            self.root.current[label_key] = f'f{i}'

    def anim_loop(self):
        self.event_init.wait()

        i = 0
        j = 0
        while self.root.run:
            if self.root.status['sap']:
                self.change_image(i, 'image')
                i += 1
                if i == 12:
                    i = 0
                # time.sleep(0.25)

            if self.root.status['proc2']:
                self.change_image(j, 'image2')
                j += 1
                if j == 12:
                    j = 0
            
            time.sleep(0.2)

    def test_show(self):
        if self.root is not None:
            print(self.root.current['image'])

    def run_sap(self):
        self.processes['sap'] = multiprocessing.Process(target=self.sap.to_sap, args=[self.root.current, self.root.status])
        self.processes['sap'].start()

    def run_proc2(self):
        self.processes['proc2'] = multiprocessing.Process(target=dummy_func, args=[self.root.current, self.root.status])
        self.processes['proc2'].start()


class SapRobot:
    def to_sap(self, currents, status):
        status['sap'] = True
        for i in range(10):
            currents['message'] = f'Running sap... {i}'
            time.sleep(0.75)
        currents['message'] = 'SAP done'
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
        self.status['proc2'] = False

        self.current['message'] = 'nic'
        self.current['message2'] = 'nic'
        self.current['image'] = None
        self.current['image2'] = None
        # self.current_image = self.c.manager.Value('i', '') #''#self.images['anim']['frame0']
        # self.current_text = self.c.manager.Value('i', 'nic')

        self.make_widgs()

    def make_widgs(self):
        self.buttons = {}
        self.labels_img = {}
        self.labels_txt = {}

        self.labels_img['image'] = Label(self)
        self.labels_img['image'].pack()

        self.labels_txt['message'] = Label(self, text=self.current['message'])
        self.labels_txt['message'].pack()

        self.buttons['run1'] = Button(self, text='Run sap', command=self.c.run_sap)
        self.buttons['run1'].pack()

        self.labels_img['image2'] = Label(self)
        self.labels_img['image2'].pack()

        self.labels_txt['message2'] = Label(self, text=self.current['message2'])
        self.labels_txt['message2'].pack()

        self.buttons['run2'] = Button(self, text='Run another process', command=self.c.run_proc2)
        self.buttons['run2'].pack()

        self.buttons['quit'] = Button(self, text='Quit', command=self._exit_app)
        self.buttons['quit'].pack(pady=10)

    def load_imgs(self):
        self.images = {}
        self.images['anim1'] = {}
        self.images['anim2'] = {}
        
        for i in range(len(os.listdir('./loading/loading_one'))):
            im = Image.open(f'loading/loading_one/f{i}.png')
            self.images['anim1'][f'f{i}'] = ImageTk.PhotoImage(im)

        for i in range(len(os.listdir('./loading/loading_two'))):
            im = Image.open(f'loading/loading_two/f{i}.png')
            self.images['anim2'][f'f{i}'] = ImageTk.PhotoImage(im)

    def _exit_app(self):
        for proc in self.c.processes.values():
            if proc is not None:
                proc.terminate()

        self.run = False

    def myloop(self):
        self.c.event_init.set()
        while self.run:
            for img in list(self.labels_img.keys()):
                if str(self.labels_img[img]['image']) != str(self.current[img]):
                    if self.current[img] is not None:
                        self.labels_img[img]['image'] = self.images['anim2'][self.current[img]]
                        # print(self.labels_img[img]['image'])
                    else:
                        self.labels_img[img]['image'] = ''

            for name in self.labels_txt.keys():
                if self.labels_txt[name]['text'] != self.current[name]:
                    self.labels_txt[name]['text'] = self.current.get(name, '')


            self.update()
            self.update_idletasks()

def main():
    c = WindowController()

    # t1 = threading.Thread(target=c.run_gui)
    # t1.start()

    t2 = threading.Thread(target=c.anim_loop, daemon=True)
    t2.start()

    c.run_gui(400,400)

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