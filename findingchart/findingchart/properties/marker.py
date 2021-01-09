from tkinter import *

import numpy as np

from .property import Property
from .option import *

class Marker (Property) :

    def __init__(self, master, removeable=True):

        super().__init__(master, removeable)

        self.set_title('Marker')

        self.ra = 0.0
        self.dec = 0.0
        self.radius = 30.0
        self.line_style = 'dotted'
        self.line_width = 1.0
        self.color = '#ffffff'
        self.alpha = 1.0

        self.t = np.linspace(0, 2*np.pi, 100)
        self.x = None
        self.y = None

        ra = Entry(self, 'R.A.', self.ra)
        ra.validate = lambda v: (v >= 0) & (v <= 360)
        ra.command = lambda v: self.set_position(ra=v)
        ra.pack(fill=X)

        dec = Entry(self, 'Dec.', self.dec)
        dec.validate = lambda v: (v >= -180) & (v <= 180)
        dec.command = lambda v: self.set_position(dec=v)
        dec.pack(fill=X)

        radius = Entry(self, 'Radius', self.radius)
        radius.validate = lambda v: (v > 0)
        radius.command = lambda v: self.set_radius(v)
        radius.pack(fill=X)

        line_style = OptionMenu(self, 'Line style', self.line_style, ['dotted', 'dashed', 'solid'])
        line_style.command = lambda v: self.set_line_style(v)
        line_style.pack(fill=X)

        line_width = Entry(self, 'Line width', self.line_width)
        line_width.validate = lambda v: (v > 0)
        line_width.command = lambda v: self.set_line_width(v)
        line_width.pack(fill=X)

        color = Entry(self, 'Color', self.color)
        color.command = lambda v: self.set_color(v)
        color.pack(fill=X)

        alpha = Entry(self, 'Alpha', self.alpha)
        alpha.validate = lambda v: (v >= 0) & (v <= 1)
        alpha.command = lambda v: self.set_alpha(v)
        alpha.pack(fill=X)

        self.draw()

    def set_position(self, ra=None, dec=None):
   
        self.ra = ra if not ra is None else self.ra
        self.dec = dec if not dec is None else self.dec
    
        try:
            x, y = self.master.filemanager.wcs.wcs_world2pix([self.ra], [self.dec], 0)
        except:
            return

        radius = self.radius / self.master.filemanager.scale
        self.x = x[0] + radius * np.cos(self.t)
        self.y = y[0] + radius * np.sin(self.t)

        self.artist.set_data(self.x, self.y)

        self.artist.set_visible(True)

        self.master.fitsviewer.canvas.draw()

    def set_radius(self, radius):

        self.radius = radius
        self.set_position()

    def set_line_style(self, line_style):

        self.line_style = line_style
        self.artist.set_linestyle(line_style)
        self.master.fitsviewer.canvas.draw()

    def set_line_width(self, line_width):

        self.line_width = line_width
        self.artist.set_linewidth(line_width)
        self.master.fitsviewer.canvas.draw()

    def set_color(self, color):

        self.artist.set_color(color)

        try:
            self.master.fitsviewer.canvas.draw()
        except Exception as e:
            self.artist.set_color(self.color)
            self.master.fitsviewer.canvas.draw()
        else:
            self.color = color

    def set_alpha(self, alpha):

        self.alpha = alpha
        self.artist.set_alpha(alpha)
        self.master.fitsviewer.canvas.draw()

    def draw(self):

        self.artist, = self.master.fitsviewer.ax.plot(0, 0,
                visible = False,
                color = self.color,
                linestyle = self.line_style,
                linewidth = self.line_width,
                alpha = self.alpha
        )

        self.set_position()

        self.master.fitsviewer.canvas.draw()

    def redraw(self):

        self.remove()
        self.draw()

    def remove(self):

        self.artist.set_visible(False)

        try:
            self.master.fitsviewer.ax.lines.remove(self.artist)
        except:
            pass
        del self.artist

        self.master.fitsviewer.canvas.draw()
