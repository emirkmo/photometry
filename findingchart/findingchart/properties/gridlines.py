from tkinter import *

from .property import Property
from .option import *

class GridLines (Property) :

    def __init__(self, master, removeable=False):

        super().__init__(master, removeable)

        self.set_title('Grid lines')

        self.line_style = 'dotted'
        self.width = 1.0
        self.color = '#ffffff'
        self.alpha = 1.0

        linestyle = OptionMenu(self, 'Line style', self.line_style, ['dotted', 'dashed', 'solid'])
        linestyle.command = lambda v: self.master.fitsviewer.set_grid_linestyle(v)
        linestyle.pack(fill=X)

        width = Entry(self, 'Width', self.width)
        width.validate = lambda v: (v > 0)
        width.command = lambda v: self.master.fitsviewer.set_grid_width(v)
        width.pack(fill=X)

        color = Entry(self, 'Color', self.color)
        color.command = lambda v: self.master.fitsviewer.set_grid_color(v)
        color.pack(fill=X)

        alpha = Entry(self, 'Alpha', self.alpha)
        alpha.validate = lambda v: (v >= 0) & (v <= 1)
        alpha.command = lambda v: self.master.fitsviewer.set_grid_alpha(v)
        alpha.pack(fill=X)
