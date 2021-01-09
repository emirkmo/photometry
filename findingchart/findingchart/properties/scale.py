from tkinter import *

import numpy as np

from .property import Property
from .option import *

class ScaleArtist () :

    def __init__(self, ax, visible, position, unit, length, width, offset,
                color, marker_sizes, scale):

        self.ax = ax

        self.visible = visible
        self.position = position
        self.unit = unit
        self.length = length
        self.width = width
        self.offset = offset
        self.color = color
        self.marker_sizes = marker_sizes

        self.scale = scale

        self.connects = [
                self.ax.callbacks.connect('xlim_changed', lambda ax: self.redraw()),
                self.ax.callbacks.connect('ylim_changed', lambda ax: self.redraw())
        ]

        self.draw()

    def set_visible(self, visible):

        self.visible = visible

        self.line.set_visible(visible)
        self.label.set_visible(visible)

    def set_position(self, position):

        self.position = position
        self.redraw()

    def set_unit(self, unit):

        self.unit = unit
        self.redraw()

    def set_length(self, length):

        self.length = length
        self.redraw()

    def set_width(self, width):

        self.width = width

        self.line.set_linewidth(width)
        self.line.set_markeredgewidth(width)

    def set_offset(self, offset):

        self.offset = offset
        self.redraw()

    def set_color(self, color):

        self.color = color

        self.line.set_color(color)
        self.label.set_color(color)

    def set_marker_sizes(self, marker_sizes):

        self.marker_sizes = marker_sizes

        self.line.set_markersize(marker_sizes)

    def draw(self):

        x, y = self.position
        scale, unit = {'Arcmin': (60, '\''), 'Arcsec': (1, '"')}[self.unit]
        length = float(self.length) * scale / self.scale / np.diff(self.ax.get_xlim())[0]

        _offset = (self.ax.transAxes.transform((0, 0)) + np.array([0, self.offset]))[1]
        offset = self.ax.transAxes.inverted().transform((0, _offset))[1]

        self.line, = self.ax.plot([x - length/2, x + length/2], [y, y],
                visible = self.visible,
                color = self.color,
                linewidth = self.width,
                marker = '|',
                markeredgewidth = self.width,
                markersize = self.marker_sizes,
                transform = self.ax.transAxes
        )
        self.label = self.ax.text(x, y + offset, self.length + unit,
                visible = self.visible,
                color = self.color,
                size = 14,
                horizontalalignment = 'center',
                verticalalignment = 'bottom',
                transform = self.ax.transAxes
        )

    def redraw(self):

        self.remove()
        self.draw()

    def remove(self):

        if hasattr(self, 'line'):

            self.line.set_visible(False)
            self.ax.lines.remove(self.line)
            del self.line

        if hasattr(self, 'label'):

            self.label.set_visible(False)
            self.ax.texts.remove(self.label)
            del self.label

class Scale (Property) :

    def __init__(self, master, removeable=False, show=False):

        super().__init__(master, removeable, show)

        self.set_title('Scale')

        self.visible = False
        self.position = 0.1, 0.1
        self.unit = 'Arcmin'
        self.length = str(1)
        self.width = 1.0
        self.offset = 0.0
        self.color = '#ffffff'
        self.marker_sizes = 5

        self.scale = None

        visible = CheckBox(self, 'Visible', self.visible)
        visible.command = lambda v: self.set_visible(v)
        visible.pack(fill=X)

        position = Entry(self, 'Position', '%.1f, %.1f' % self.position)
        position.validate = lambda v: len(list(map(float, v.split(',')))) == 2
        position.command = lambda v: self.set_position(list(map(float, v.split(','))))
        position.pack(fill=X)

        unit = OptionMenu(self, 'Unit', self.unit, ['Arcmin', 'Arcsec'])
        unit.command = lambda v: self.set_unit(v)
        unit.pack(fill=X)

        length = Entry(self, 'Length', self.length)
        length.validate = lambda v: float(v)
        length.command = lambda v: self.set_length(v)
        length.pack(fill=X)

        width = Entry(self, 'Width', self.width)
        width.validate = lambda v: (v > 0)
        width.command = lambda v: self.set_width(v)
        width.pack(fill=X)

        offset = Entry(self, 'Offset', self.offset)
        offset.command = lambda v: self.set_offset(v)
        offset.pack(fill=X)

        color = Entry(self, 'Color', '#ffffff')
        color.command = lambda v: self.set_color(v)
        color.pack(fill=X)

        marker_sizes = Entry(self, 'Marker sizes', self.marker_sizes)
        marker_sizes.validate = lambda v: (v >= 0)
        marker_sizes.command = lambda v: self.set_marker_sizes(v)
        marker_sizes.pack(fill=X)

    def initialize(self):

        self.scale = self.master.filemanager.scale

        self.artist = ScaleArtist(self.master.fitsviewer.ax,
                visible = self.visible,
                position = self.position,
                unit = self.unit,
                length = self.length,
                width = self.width,
                offset = self.offset,
                color = self.color,
                marker_sizes = self.marker_sizes,
                scale = self.scale,
        )

    def set_visible(self, visible):

        self.visible = visible
        self.artist.set_visible(visible)
        self.master.fitsviewer.canvas.draw()

    def set_position(self, position):

        self.position = position
        self.artist.set_position(position)
        self.master.fitsviewer.canvas.draw()

    def set_unit(self, unit):

        self.unit = unit
        self.artist.set_unit(unit)
        self.master.fitsviewer.canvas.draw()

    def set_length(self, length):

        self.length = length
        self.artist.set_length(length)
        self.master.fitsviewer.canvas.draw()

    def set_width(self, width):

        self.width = width
        self.artist.set_width(width)
        self.master.fitsviewer.canvas.draw()

    def set_offset(self, offset):

        self.offset = offset
        self.artist.set_offset(offset)
        self.master.fitsviewer.canvas.draw()

    def set_color(self, color):

        try:
            self.artist.set_color(color)
            self.master.fitsviewer.canvas.draw()
        except:
            self.artist.set_color(self.color)
            self.master.fitsviewer.canvas.draw()
        else:
            self.color = color

    def set_marker_sizes(self, marker_sizes):

        self.marker_sizes = marker_sizes
        self.artist.set_marker_sizes(marker_sizes)
        self.master.fitsviewer.canvas.draw()

    def draw(self):

        self.initialize()
        self.master.fitsviewer.canvas.draw()

    def redraw(self):

        self.artist.remove()
        del self.artist

        self.draw()
