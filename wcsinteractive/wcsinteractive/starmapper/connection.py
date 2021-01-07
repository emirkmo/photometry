import numpy as np

from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch

from .blitfigure import BlitFigure

class Connection () :

    def __init__(self, master, ax, x, y):

        self.master = master
        self.ax0 = ax
        self.x0, self.y0 = x, y

        self.scat = [ax.scatter(x, y, c=[], s=200, linewidth=1.5, edgecolors=(.25, .25, 1))]
        self.master.add_artist(self.scat[0])

        x0, y0 = (ax.transData + self.master.transFigure.inverted()).transform((x, y))
        self.line = Line2D([x0], [y0], color=(.25, .25, 1), transform=self.master.transFigure)
        self.master.add_artist(self.line)

    def set_xy(self, ax, x, y):

        self.axx = ax

        if ax:
            self.xx, self.yy = x, y
            xx, yy = (ax.transData + self.master.transFigure.inverted()).transform((x, y))
        else:
            xx, yy = self.master.transFigure.inverted().transform((x, y))

        x0, y0 = list(zip(*self.line.get_data()))[0]
        self.line.set_data([x0, xx], [y0, yy])

    def define(self):

        self.con = ConnectionPatch(lw=1.5, color=(.25, .25, 1), picker=10,
                xyA=(self.x0, self.y0), coordsA='data', axesA=self.ax0,
                xyB=(self.xx, self.yy), coordsB='data', axesB=self.axx)
        self.con.parent = self
        super(BlitFigure, self.master).add_artist(self.con)
        self.master.add_artist(self.con)

        self.scat += [self.axx.scatter(self.xx, self.yy, c=[], s=200, linewidth=1.5, edgecolors=(.25, .25, 1))]
        self.master.add_artist(self.scat[-1])

        self.master.del_artist(self.line)
        del self.line

    def get_xy(self):

        return { self.ax0 : (self.x0, self.y0) , self.axx : (self.xx, self.yy) }

    def set_color(self, color):

        self.con.set_color(color)

        for scat in self.scat:
            scat.set_edgecolors(color)

    def remove(self):

        while self.scat:
            self.master.del_artist(self.scat.pop())
       
        if hasattr(self, 'line'):

            self.master.del_artist(self.line)
        
        if hasattr(self, 'con'):

            self.con.remove()
            self.master.del_artist(self.con)
