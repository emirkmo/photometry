from tkinter import *

import numpy as np

from .property import Property
from .option import *

class CompassArtist () :

    def __init__(self, ax, visible, position, indicators, offset, color,
                arrow_lengths, arrow_widths, theta, flip_h, flip_v):

        self.ax = ax

        self.visible = visible
        self.position = position
        self.indicators = indicators
        self.offset = offset
        self.color = color
        self.arrow_lengths = arrow_lengths
        self.arrow_widths = arrow_widths

        self.theta = theta
        self.flip_h = flip_h
        self.flip_v = flip_v

        self.connects = [
                self.ax.callbacks.connect('xlim_changed', lambda ax: self.redraw()),
                self.ax.callbacks.connect('ylim_changed', lambda ax: self.redraw())
        ]

        self.draw()

    def set_visible(self, visible):

        self.visible = visible

        for arrow in self.arrow:
            arrow.set_visible(visible)

        for label in self.label:
            label.set_visible(visible)

    def set_position(self, position):

        self.position = position
        self.redraw()

    def set_indicators(self, indicators):

        self.indicators = indicators
        self.redraw()

    def set_offset(self, offset):

        self.offset = offset
        self.redraw()

    def set_color(self, color):

        self.color = color

        for arrow in self.arrow:
            arrow.set_color(color)

        for label in self.label:
            label.set_color(color)

    def set_arrow_lengths(self, arrow_lengths):

        self.arrow_lengths = arrow_lengths
        self.redraw()

    def set_arrow_widths(self, arrow_widths):

        self.arrow_widths = arrow_widths
        self.redraw()

    def draw(self):

        rot = np.array([[np.cos(-self.theta), np.sin(-self.theta)], [-np.sin(-self.theta), np.cos(-self.theta)]])
        dx, dy = 1, np.diff(self.ax.get_xlim())[0] / np.diff(self.ax.get_ylim())[0]

        ns, ew = [{'N': +1, 'S': -1, 'E': -1, 'W': +1}[i] for i in list(self.indicators)]

        ns_length = self.flip_v * self.arrow_lengths * rot.dot([0, ns]) * np.array([dx, dy])
        ew_length = self.flip_h * self.arrow_lengths * rot.dot([ew, 0]) * np.array([dx, dy])

        arrow_widths = np.diff(self.ax.transAxes.inverted().transform([(0, 0), (self.arrow_widths, 0)])[:,0])[0]
        ns_width, ew_width = arrow_widths * np.sqrt(np.power(rot, 2).dot(np.power([dx, dy], 2)))
        ns_head_width, ew_head_width = 3 * ns_width, 3 * ew_width
        ns_head_length, ew_head_length = 1.5 * ew_head_width, 1.5 * ns_head_width

        ns_position = self.position - ew_head_width / 2 * ns_length / np.sqrt(np.power(ns_length, 2).sum())
        ew_position = self.position - ns_head_width / 2 * ew_length / np.sqrt(np.power(ew_length, 2).sum())

        self.arrow = [
            self.ax.arrow(*ns_position, *ns_length,
                    visible = self.visible,
                    color = self.color,
                    width = ns_width,
                    head_width = ns_head_width,
                    head_length = ns_head_length,
                    transform = self.ax.transAxes
            ),
            self.ax.arrow(*ew_position, *ew_length,
                    visible = self.visible,
                    color = self.color,
                    width = ew_width,
                    head_width = ew_head_width,
                    head_length = ew_head_length,
                    transform = self.ax.transAxes
            )
        ]

        self.label = [
            self.ax.text(*(self.position + self.offset * ns_length), self.indicators[0],
                    visible = self.visible,
                    color = self.color,
                    size = 14,
                    horizontalalignment = 'center',
                    verticalalignment = 'center',
                    transform = self.ax.transAxes
            ),
            self.ax.text(*(self.position + self.offset * ew_length), self.indicators[1],
                    visible = self.visible,
                    color = self.color,
                    size = 14,
                    horizontalalignment = 'center',
                    verticalalignment = 'center',
                    transform = self.ax.transAxes
            ),
        ]

    def redraw(self):

        self.remove()
        self.draw()

    def remove(self):

        while len(self.arrow):

            arrow = self.arrow.pop()
            arrow.set_visible(False)
            self.ax.patches.remove(arrow)
            del arrow

        while len(self.label):

            label = self.label.pop()
            label.set_visible(False)
            self.ax.texts.remove(label)
            del label

class Compass (Property) :

    def __init__(self, master, removeable=False, show=False):

        super().__init__(master, removeable, show)

        self.set_title('Compass')

        self.visible = False
        self.position = 0.9, 0.1
        self.indicators = 'NE'
        self.offset = 1.25
        self.color = '#ffffff' 
        self.arrow_lengths = 0.2
        self.arrow_widths = 1.0

        self.theta = None
        self.flip_h = None
        self.flip_v = None

        visible = CheckBox(self, 'Visible', self.visible)
        visible.command = lambda v: self.set_visible(v)
        visible.pack(fill=X)

        position = Entry(self, 'Position', '%.1f, %.1f' % self.position)
        position.validate = lambda v: len(list(map(float, v.split(',')))) == 2
        position.command = lambda v: self.set_position(list(map(float, v.split(','))))
        position.pack(fill=X)

        indicators = OptionMenu(self, 'Indicators', self.indicators, ['NE', 'NW', 'SE', 'SW'])
        indicators.command = lambda v: self.set_indicators(v)
        indicators.pack(fill=X)

        offset = Entry(self, 'Offset', self.offset)
        offset.command = lambda v: self.set_offset(v)
        offset.pack(fill=X)

        color = Entry(self, 'Color', '#ffffff')
        color.command = lambda v: self.set_color(v)
        color.pack(fill=X)

        arrow_lengths = Entry(self, 'Arrow lengths', self.arrow_lengths)
        arrow_lengths.validate = lambda v: (v > 0)
        arrow_lengths.command = lambda v: self.set_arrow_lengths(v)
        arrow_lengths.pack(fill=X)

        arrow_widths = Entry(self, 'Arrow widths', self.arrow_widths)
        arrow_widths.validate = lambda v: (v >= 0)
        arrow_widths.command = lambda v: self.set_arrow_widths(v)
        arrow_widths.pack(fill=X)

    def initialize(self):

        self.theta = self.master.filemanager.theta
        self.flip_h = self.master.filemanager.flip_h
        self.flip_v = self.master.filemanager.flip_v

        self.artist = CompassArtist(self.master.fitsviewer.ax,
                visible = self.visible,
                position = self.position,
                indicators = self.indicators,
                offset = self.offset,
                color = self.color,
                arrow_lengths = self.arrow_lengths,
                arrow_widths = self.arrow_widths,
                theta = self.theta,
                flip_h = self.flip_h,
                flip_v = self.flip_v,
        )

    def set_visible(self, visible):

        self.visible = visible
        self.artist.set_visible(visible)
        self.master.fitsviewer.canvas.draw()

    def set_position(self, position):

        self.position = position
        self.artist.set_position(position)
        self.master.fitsviewer.canvas.draw()

    def set_indicators(self, indicators):

        self.indicators = indicators
        self.artist.set_indicators(indicators)
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

    def set_arrow_lengths(self, arrow_lengths):

        self.arrow_lengths = arrow_lengths
        self.artist.set_arrow_lengths(arrow_lengths)
        self.master.fitsviewer.canvas.draw()

    def set_arrow_widths(self, arrow_widths):

        self.arrow_widths = arrow_widths
        self.artist.set_arrow_widths(arrow_widths)
        self.master.fitsviewer.canvas.draw()

    def draw(self):

        self.initialize()
        self.master.fitsviewer.canvas.draw()

    def redraw(self):

        self.artist.remove()
        del self.artist

        self.draw()
