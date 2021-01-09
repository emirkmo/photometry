from tkinter import *

import numpy as np

from astropy.io import fits

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class FITSViewer (Figure) :

    def __init__(self, *args, **kwargs):

        self.frame = Frame(*args, **kwargs)
        self.frame.pack_propagate(False)

        super().__init__()

        self.grid_color = '#ffffff'
        self.grid_linestyle = 'dotted'
        self.grid_alpha = 1.
        self.grid_linewidth = 1.

        self.canvas = FigureCanvasTkAgg(self, master=self.frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=BOTH, side=TOP)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)

        self.set_data(np.zeros((1, 1)), None)

        self.filemanager = None
        self.properties = None

    def set_grid_linestyle(self, linestyle):

        self.grid_linestyle = linestyle

        if not self.grid_color == '':
            self.ax.grid(True, color=self.grid_color, linestyle=linestyle, alpha=self.grid_alpha, linewidth=self.grid_linewidth)

        self.canvas.draw()

    def set_grid_color(self, color):

        self.grid_color = color
        self.ax.grid(color=color, linestyle=self.grid_linestyle, alpha=self.grid_alpha, linewidth=self.grid_linewidth)

        try:
            self.canvas.draw()
        except Exception as e:
            self.grid_color = ''
            self.ax.grid(False)
            self.canvas.draw()

    def set_grid_alpha(self, alpha):

        self.grid_alpha = alpha

        if not self.grid_color == '':
            self.ax.grid(True, color=self.grid_color, linestyle=self.grid_linestyle, alpha=alpha, linewidth=self.grid_linewidth)

        self.canvas.draw()

    def set_grid_width(self, linewidth):

        self.grid_linewidth = linewidth

        if not self.grid_color == '':
            self.ax.grid(True, color=self.grid_color, linestyle=self.grid_linestyle, alpha=self.grid_alpha, linewidth=linewidth)

        self.canvas.draw()

    def set_data(self, data, wcs, reset_limits=False):

        xlim = ylim = None

        if hasattr(self, 'ax'):

            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()

            if [xlim, ylim] == [(-.5, .5), (.5, -.5)]:
                xlim = ylim = None

            self.ax.remove()

        if np.prod(np.array(data).shape[:2]) == 1:

            wcs = None
            xlim = ylim = None

        if reset_limits:

            xlim = ylim = None

        self.ax = self.add_subplot(111, projection=wcs)

        self.image = self.ax.imshow(data, cmap='gray')

        self.ax.set_xlabel('Right Ascension')
        self.ax.set_ylabel('Declination')

        if not self.grid_color == '':
            self.ax.grid(True, color=self.grid_color, linestyle=self.grid_linestyle, alpha=self.grid_alpha, linewidth=self.grid_linewidth)

        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        if hasattr(self.properties, 'properties'):
            for obj in self.properties.properties:
                if hasattr(obj, 'redraw'):
                    obj.redraw()

        self.canvas.draw()

    def pack(self, *args, **kwargs):

        self.frame.pack(*args, **kwargs)
