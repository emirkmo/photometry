from tkinter import *

from .property import Property
from .option import *

class ImageData (Property) :

    def __init__(self, master, removeable=False):

        super().__init__(master, removeable)

        self.set_title('Image data')

        self.mode = 'B&W'
        self.scale = 1.0
        self.rotation = 0.0
        self.flip_h = False
        self.flip_v = False

        mode = OptionMenu(self, 'Mode', self.mode, ['B&W', 'RGB'])
        mode.command = lambda v: self.master.filemanager.set_mode(v)
        mode.pack(fill=X)

        scale = Entry(self, 'Scale', self.scale)
        scale.validate = lambda v: (v > 0)
        scale.command = lambda v: self.master.filemanager.set_scale(v)
        scale.pack(fill=X)

        rotation = Entry(self, 'Rotation', self.rotation)
        rotation.command = lambda v: self.master.filemanager.set_rotation(v)
        rotation.pack(fill=X)

        flip_h = CheckBox(self, 'Flip R.A.', self.flip_h)
        flip_h.command = lambda v: self.master.filemanager.set_flip(h=v)
        flip_h.pack(fill=X)

        flip_v = CheckBox(self, 'Flip Dec.', self.flip_v)
        flip_v.command = lambda v: self.master.filemanager.set_flip(v=v)
        flip_v.pack(fill=X)
