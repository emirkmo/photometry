from tkinter import *

import numpy as np

from .property import Property
from .option import *

class Inset (Property) :

    def __init__(self, master, removeable=False, show=False):

        super().__init__(master, removeable, show)

        self.set_title('Inset')

        self.visible = False
        self.position = 0.6, 0.6
        self.size = 0.3, 0.3
        self.quantile = 0.1, 0.9
        self.invert = True

        visible = CheckBox(self, 'Visible', self.visible)
        visible.command = lambda v: self.set_visible(v)
        visible.pack(fill=X)

        position = Entry(self, 'Position', '%.1f, %.1f' % self.position)
        position.validate = lambda v: len(list(map(float, v.split(',')))) == 2
        position.command = lambda v: self.set_position(list(map(float, v.split(','))))
        position.pack(fill=X)

        size = Entry(self, 'Size', '%.1f, %.1f' % self.size)
        size.validate = lambda v: len(list(map(float, v.split(',')))) == 2
        size.command = lambda v: self.set_size(list(map(float, v.split(','))))
        size.pack(fill=X)

        def validate_quantile(v):
            qmin, qmax = list(map(float, v.split(',')))
            return 0 <= qmin < qmax <= 1

        quantile = Entry(self, 'Quantile', '%.1f, %.1f' % self.quantile)
        quantile.validate = validate_quantile
        quantile.command = lambda v: self.set_quantile(list(map(float, v.split(','))))
        quantile.pack(fill=X)

        invert = CheckBox(self, 'Invert', self.invert)
        invert.command = lambda v: self.set_invert(v)
        invert.pack(fill=X)

    def initialize(self):

        self.image = self.master.filemanager.image

        if self.invert:
            image = np.min(self.image) + np.max(self.image) - self.image
        else:
            image = self.image

        self.ax = self.master.fitsviewer.add_axes(list(self.position) + list(self.size),
                visible=self.visible, zorder=1)

        self.ax.set_xticks([])
        self.ax.set_yticks([])

        if np.prod(np.shape(self.image)[:2]) == 1:

            clim = -1, 0
            image = np.zeros((1, 1))

        else:

            clim = np.quantile(image, self.quantile)

        self.artist = self.ax.imshow(image,
                cmap = 'gray',
                clim = clim,
                origin = 'lower',
                aspect = 'equal'
        )

    def set_visible(self, visible):

        self.visible = visible
        self.ax.set_visible(visible)
        self.master.fitsviewer.canvas.draw()

    def set_position(self, position):

        self.position = position
        self.ax.set_position(list(self.position) + list(self.size))
        self.master.fitsviewer.canvas.draw()

    def set_size(self, size):

        self.size = size
        self.ax.set_position(list(self.position) + list(self.size))
        self.master.fitsviewer.canvas.draw()

    def set_quantile(self, quantile):

        self.quantile = quantile

        if self.invert:
            image = np.min(self.image) + np.max(self.image) - self.image
        else:
            image = self.image
        clim = np.quantile(image, quantile)

        self.artist.set_clim(clim)
        self.master.fitsviewer.canvas.draw()

    def set_invert(self, invert):

        self.invert = invert

        if self.invert:
            image = np.min(self.image) + np.max(self.image) - self.image
        else:
            image = self.image
        clim = np.quantile(image, self.quantile)

        self.artist.set_data(image)
        self.artist.set_clim(clim)
        self.master.fitsviewer.canvas.draw()

    def draw(self):

        self.initialize()
        self.master.fitsviewer.canvas.draw()

    def redraw(self):

        self.ax.remove()
        del self.ax

        self.draw()
