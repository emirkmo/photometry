from tkinter import *

import numpy as np

from .property import Property
from .option import *

class Text (Property) :

    def __init__(self, master, removeable=True):

        super().__init__(master, removeable)

        self.set_title('Text')

        self.text = 'Text'
        self.ra = 0.0
        self.dec = 0.0
        self.anchor = 'Center center'
        self.offset = 0.0, 0.0
        self.color = '#ffffff'
        self.size = 12

        self.x = None
        self.y = None

        text = Entry(self, 'Text', self.text)
        text.command = lambda v: self.set_text(v)
        text.pack(fill=X)

        ra = Entry(self, 'R.A.', self.ra)
        ra.validate = lambda v: (v >= 0) & (v <= 360)
        ra.command = lambda v: self.set_position(ra=v)
        ra.pack(fill=X)

        dec = Entry(self, 'Dec.', self.dec)
        dec.validate = lambda v: (v >= -180) & (v <= 180)
        dec.command = lambda v: self.set_position(dec=v)
        dec.pack(fill=X)

        anchor_options = ['%s %s' % (v, h)
                for v in ('Center', 'Top', 'Bottom')
                for h in ('center', 'left', 'right')
        ]

        anchor = OptionMenu(self, 'Anchor', self.anchor, anchor_options)
        anchor.command = lambda v: self.set_anchor(v)
        anchor.pack(fill=X)

        offset = Entry(self, 'Offset', '%.2f, %.2f' % self.offset)
        offset.validate = lambda v: len(list(map(float, v.split(',')))) == 2
        offset.command = lambda v: self.set_position(offset=list(map(float, v.split(','))))
        offset.pack(fill=X)

        color = Entry(self, 'Color', self.color)
        color.command = lambda v: self.set_color(v)
        color.pack(fill=X)

        size = Entry(self, 'Size', self.size)
        size.validate = lambda v: (v > 0)
        size.command = lambda v: self.set_size(v)
        size.pack(fill=X)

        self.draw()

    def set_text(self, text):

        self.text = text
        self.artist.set_text(text)
        self.master.fitsviewer.canvas.draw()

    def set_position(self, ra=None, dec=None, offset=None):
   
        self.ra = ra if not ra is None else self.ra
        self.dec = dec if not dec is None else self.dec
        self.offset = offset if not offset is None else self.offset

        try:
            x, y = self.master.filemanager.wcs.wcs_world2pix([self.ra], [self.dec], 0)
        except:
            return

        self.x = x[0] + self.offset[0]
        self.y = y[0] + self.offset[1]

        self.artist.set_position((self.x, self.y))

        self.artist.set_visible(True)

        self.master.fitsviewer.canvas.draw()

    def set_anchor(self, anchor):

        self.anchor = anchor
        va, ha = list(map(str.lower, anchor.split()))

        self.artist.set_horizontalalignment(ha)
        self.artist.set_verticalalignment(va)
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

    def set_size(self, size):

        self.size = size
        self.artist.set_size(size)
        self.master.fitsviewer.canvas.draw()

    def draw(self):

        self.artist = self.master.fitsviewer.ax.text(0, 0, self.text,
                visible = False,
                size = self.size,
                color = self.color
        )

        self.set_anchor(self.anchor)
        self.set_position()

        self.master.fitsviewer.canvas.draw()

    def redraw(self):

        self.remove()
        self.draw()

    def remove(self):

        self.artist.set_visible(False)

        try:
            self.master.fitsviewer.ax.texts.remove(self.artist)
        except:
            pass
        del self.artist

        self.master.fitsviewer.canvas.draw()
