from tkinter import *

import numpy as np

class File (Frame) :

    def __init__(self, master, filename, data, wcs):

        super().__init__(master, padx=10)

        self.remove = Button(self, text='X', width=0, padx=4, pady=0, background='red', command=self.remove)
        self.filename = Label(self, text=filename, width=23, anchor=W)

        self.data, self._data = data, data.copy()
        self.wcs = wcs

        self.vmin, self._vmin = 0.01, Entry(self, width=4)
        self._vmin.bind("<KeyRelease>", self.set_vmin)
        self.vmax, self._vmax = 0.99, Entry(self, width=4)
        self._vmax.bind("<KeyRelease>", self.set_vmax)
        self.weight, self._weight = 1.0, Entry(self, width=3)
        self._weight.bind("<KeyRelease>", self.set_weight)

        self._vmin.insert(0, self.vmin)
        self._vmax.insert(0, self.vmax)
        self._weight.insert(0, self.weight)

        self.remove.pack(side=LEFT)
        self.filename.pack(side=LEFT)
        self._weight.pack(side=RIGHT)
        self._vmax.pack(side=RIGHT)
        self._vmin.pack(side=RIGHT)

        self.update_data()

    def set_vmin(self, e):

        try:
            v = float(e.widget.get())
            assert 0 <= v <= self.vmax
        except:
            e.widget['background'] = 'red'
            return
        else:
            e.widget['background'] = 'white'

        if v == self.vmin:
            return
        self.vmin = v

        self.update_data()
        self.master.update_data()
        self.master.update_image()
        self.master.master.update_image()

    def set_vmax(self, e):

        try:
            v = float(e.widget.get())
            assert self.vmin <= v <= 1
        except:
            e.widget['background'] = 'red'
            return
        else:
            e.widget['background'] = 'white'

        if v == self.vmax:
            return
        self.vmax = v

        self.update_data()
        self.master.update_data()
        self.master.update_image()
        self.master.master.update_image()

    def set_weight(self, e):

        try:
            v = float(e.widget.get())
            assert 0 < v
        except:
            e.widget['background'] = 'red'
            return
        else:
            e.widget['background'] = 'white'

        if v == self.weight:
            return
        self.weight = v

        self.update_data()
        self.master.update_data()
        self.master.update_image()
        self.master.master.update_image()

    def update_data(self):

        self.data = self.weight * self._data.copy()

        vmin, vmax = np.nanquantile(self.data, (self.vmin, self.vmax))
        self.data[self.data < vmin] = vmin
        self.data[self.data > vmax] = vmax

        self.data_changed = True

    def remove(self):

        self.master.files.remove(self)

        self.pack_forget()
        self.destroy()

        for fg in self.master.master.filegroups:
            for f in fg.files:
                f.data_changed = True

        self.master.master.register_data()
        self.master.update_data()
        self.master.update_image()
        self.master.master.update_image()
