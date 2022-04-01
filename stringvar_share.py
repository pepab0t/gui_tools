import multiprocessing
import threading
from totalsapfunctions import SapAccess
from tkinter import *
import time
import random

class Wnd(Tk):
    def __init__(self, width, height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry(f'{width}x{height}')
        self.run = True

        self.label_str = StringVar()
        self.label_str.set('Ahoj')
        
        self.texts = multiprocessing.Manager().dict({str(self.label_str): None})

        self.label_title = Label(self, textvariable=self.label_str)
        self.label_title.pack()

        self.button_quit = Button(self, text='Quit', command=lambda: self._exit_app(self.p2))
        self.button_quit.pack()

        # WITH MULTITHREADING IS POSSIBLE TO SHARE STRINGVAR
        # self.p1 = threading.Thread(target=dummy_func, args=(self.label_str,))
        # self.p1.start()

        self.p2 = multiprocessing.Process(target=dummy_func, args=(self.texts, str(self.label_str)) )
        self.p2.start()


    def _exit_app(self, *processes):
        for p in processes:
            p.terminate()
        self.run = False
        # self.destroy()

    def update_text(self, *variables):
        for var in variables:
            val = self.texts[str(var)]
            if val is not None:
                var.set(str(val))

    def my_loop(self):
        while self.run:
            self.update_text(self.label_str)

            self.update()
            self.update_idletasks()

def dummy_func(d, textvar):
    source = [chr(x) for x in range(65, 91)]
    
    for _ in range(10):
        d[textvar] = ''.join(random.choices(source,k=5))
        time.sleep(1)

def main():
    w = Wnd(200,200)
    w.my_loop()

    # w.mainloop()

if __name__ == "__main__":
    multiprocessing.freeze_support() ### THIS IS THE KEY !!!!
    main()