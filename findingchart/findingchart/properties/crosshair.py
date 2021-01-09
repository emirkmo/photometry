from tkinter import *

import numpy as np

from .property import Property
from .option import *

class Crosshair (Property) :

    def __init__(self, master, removeable=True):

        super().__init__(master, removeable)

        self.set_title('Crosshair')

        self.ra = 0.0
        self.dec = 0.0
        self.distance = 30.0
        self.size = 120.0
        self.line_width = 1.0
        self.color = '#ffffff'
        self.in_inset = False

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

        distance = Entry(self, 'Distance', self.distance)
        distance.validate = lambda v: (v >= 0)
        distance.command = lambda v: self.set_distance(v)
        distance.pack(fill=X)

        size = Entry(self, 'Size', self.size)
        size.validate = lambda v: (v > 0)
        size.command = lambda v: self.set_size(v)
        size.pack(fill=X)

        line_width = Entry(self, 'Line width', self.line_width)
        line_width.validate = lambda v: (v > 0)
        line_width.command = lambda v: self.set_line_width(v)
        line_width.pack(fill=X)

        color = Entry(self, 'Color', self.color)
        color.command = lambda v: self.set_color(v)
        color.pack(fill=X)

        in_inset = CheckBox(self, 'In inset', self.in_inset)
        in_inset.command = lambda v: self.set_in_inset(v)
        in_inset.pack(fill=X)

        self.draw()

    def set_in_inset(self, in_inset):

        if in_inset is self.in_inset:
            return

        self.in_inset = in_inset
        self.redraw()

    def set_position(self, ra=None, dec=None):
   
        self.ra = ra if not ra is None else self.ra
        self.dec = dec if not dec is None else self.dec
   
        try:

            distance, size = np.array([self.distance, self.size]) * self.master.filemanager.scale
            x, y = self.master.filemanager.wcs.wcs_world2pix([self.ra], [self.dec], 0)

        except Exception as e:

            return

        rot = lambda t: np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])

        t = np.linspace(0, 2*np.pi, 4, endpoint=False)
        for i, artist in enumerate(self.artist):

            dx, dy = rot(t[i]).dot([(distance, distance + size), (0, 0)])
            artist.set_data(x + dx, y + dy)

            artist.set_visible(True)

        self.master.fitsviewer.canvas.draw()

    def set_distance(self, distance):

        self.distance = distance
        self.set_position()

    def set_size(self, size):

        self.size = size
        self.set_position()

    def set_line_width(self, line_width):

        self.line_width = line_width
        for artist in self.artist:
            artist.set_linewidth(line_width)
        self.master.fitsviewer.canvas.draw()

    def set_color(self, color):

        for artist in self.artist:
            artist.set_color(color)

        try:
            self.master.fitsviewer.canvas.draw()
        except Exception as e:
            for artist in self.artist:
                artist.set_color(self.color)
            self.master.fitsviewer.canvas.draw()
        else:
            self.color = color

    def draw(self):

        self.artist = 4 * [None]

        if self.in_inset:
            ax = self.master.inset.ax
        else:
            ax = self.master.fitsviewer.ax

        for i in range(4):

            self.artist[i], = ax.plot(0, 0,
                    visible = False,
                    color = self.color,
                    linewidth = self.line_width
            )

        self.set_position()

        self.master.fitsviewer.canvas.draw()

    def redraw(self):

        self.remove()
        self.draw()

    def remove(self):

        while len(self.artist):

            artist = self.artist.pop()

            artist.set_visible(False)

            try:
                self.master.fitsviewer.ax.lines.remove(artist)
            except:
                pass

            try:
                self.master.inset.ax.lines.remove(artist)
            except:
                pass

        self.master.fitsviewer.canvas.draw()
