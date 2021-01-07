from tkinter import *

import numpy as np

from .setting import Setting
from .option import *

class Image (Setting) :

    def __init__(self, master, removeable=True):

        super().__init__(master, removeable)

        self.set_title('Image')

        self.obs_year = 2000.0
        self.scale = 1.0
        self.seeing = 1.0
        self.threshold = 1.0
        self.max_stars = 100
        self.quantile = 0.01, 0.99

        self.widgets = type('Widgets', (object,), dict())

        open_image = Button(self, 'Open image')
        open_image.command = lambda: self.master.starmapper.open_image()
        open_image.pack(fill=X)

        self.widgets.obs_year = Entry(self, 'Obs. year', self.obs_year)
        self.widgets.obs_year.validate = lambda v: (v > 1900) & (v < 2100)
        self.widgets.obs_year.command = lambda v: self.set_obs_year(v)
        self.widgets.obs_year.pack(fill=X)

        self.widgets.scale = Entry(self, 'Scale', self.scale)
        self.widgets.scale.validate = lambda v: (v > 0)
        self.widgets.scale.command = lambda v: self.set_scale(v)
        self.widgets.scale.pack(fill=X)

        self.widgets.seeing = Entry(self, 'Seeing', self.seeing)
        self.widgets.seeing.validate = lambda v: (v > 0)
        self.widgets.seeing.command = lambda v: self.set_seeing(v)
        self.widgets.seeing.pack(fill=X)

        self.widgets.threshold = Entry(self, 'Threshold', self.threshold)
        self.widgets.threshold.validate = lambda v: (v > 0)
        self.widgets.threshold.command = lambda v: self.set_threshold(v)
        self.widgets.threshold.pack(fill=X)

        max_stars = Entry(self, 'Max. stars', self.max_stars)
        max_stars.validate = lambda v: (v > 0)
        max_stars.command = lambda v: self.set_max_stars(v)
        max_stars.pack(fill=X)

        self.widgets.find_stars = Button(self, 'Find stars')
        self.widgets.find_stars.command = lambda: self.master.starmapper.find_stars()
        self.widgets.find_stars.set_disabled(True)
        self.widgets.find_stars.pack(fill=X)

    def set_obs_year(self, obs_year):

        if obs_year != self.widgets.obs_year.get():
            self.widgets.obs_year.set(obs_year)

        self.obs_year = obs_year

    def set_scale(self, scale):

        if scale != self.widgets.scale.get():
            self.widgets.scale.set(scale)

        self.scale = scale

    def set_seeing(self, seeing):

        if seeing != self.widgets.seeing.get():
            self.widgets.seeing.set(seeing)

        self.seeing = seeing

    def set_threshold(self, threshold):

        if threshold != self.widgets.threshold.get():
            self.widgets.threshold.set(threshold)

        self.threshold = threshold

    def set_max_stars(self, max_stars):

        self.max_stars = max_stars
