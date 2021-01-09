from tkinter import *
from tkinter.messagebox import showerror

import numpy as np

from astropy.wcs import WCS

from ..scrollableframe import ScrollableFrame

from .filegroup import FileGroup

class FileManager (ScrollableFrame) :

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.scale = 1
        self.theta = 0
        self.flip_h = 1
        self.flip_v = 1

        self.mode = None
        self.filegroups = []
        self.set_mode('B&W')

        self.fitsviewer = None
        self.properties = None

    def set_scale(self, scale):

        if self.scale == scale:
            return
        else:
            self.scale = scale

        self.register_data()
        self.update_data()
        self.update_image(reset_limits=True)

    def set_rotation(self, theta):

        if self.theta == np.deg2rad(theta):
            return
        else:
            self.theta = np.deg2rad(theta)

        self.register_data()
        self.update_data()
        self.update_image(reset_limits=True)

    def set_flip(self, h=None, v=None):

        self.flip_h = {True:-1, False:+1}[h] if not h is None else self.flip_h
        self.flip_v = {True:-1, False:+1}[v] if not v is None else self.flip_v

        self.register_data()
        self.update_data()
        self.update_image()

    def set_mode(self, mode):

        if self.mode == mode:
            return
        self.mode = mode

        while len(self.filegroups):
            fg = self.filegroups.pop()
            fg.pack_forget()
            fg.destroy()
            del fg

        if self.mode == 'B&W':
            self.filegroups = [
                FileGroup(self, title='Luminance'),
            ]
        elif self.mode == 'RGB':
            self.filegroups = [
                FileGroup(self, title='Red'),
                FileGroup(self, title='Green'),
                FileGroup(self, title='Blue'),
            ]
        else:
            self.filegroups = []

        self.image = [fg.image for fg in self.filegroups]

        for fg in self.filegroups:
            fg.pack(fill=X, padx=5, pady=5)

        if hasattr(self, 'fitsviewer') and self.fitsviewer:
            self.register_data()
            self.update_data()
            self.update_image(reset_limits=True)

    def update_image(self, reset_limits=False):

        self.image = np.dstack([fg.image for fg in self.filegroups])
        self.image -= np.nanmin(self.image)
        self.image /= np.nanmax(self.image) if np.nanmax(self.image) else 1

        self.fitsviewer.set_data(self.image, self.wcs, reset_limits)

    def update_data(self):

        for fg in self.filegroups:
            for f in fg.files:
                f.data_changed = True

            fg.update_data()
            fg.update_image()

    def register_data(self):

        worlds, pixels = [], []

        if not all([len(fg.files) for fg in self.filegroups]):

            for fg in self.filegroups:
                fg.data = fg.image = np.zeros((1,1))

            self.wcs = None

            return

        self.wcs = WCS()
        self.wcs.wcs.ctype = 'RA---TAN', 'DEC--TAN'
        self.wcs.wcs.pc = np.array([
            [-np.cos(self.theta), -np.sin(self.theta)],
            [-np.sin(self.theta), +np.cos(self.theta)]
        ]) * self.scale / 60 / 60
        self.wcs.wcs.cdelt = self.flip_h, self.flip_v
        self.wcs.wcs.crpix = 0, 0

        for fg in self.filegroups:

            for f in fg.files:

                (y0, x0), (yy, xx) = (0, 0), f.data.shape
                pix = [(x0, y0), (x0, yy), (xx, yy), (xx, y0)]
                sky = list(zip(*f.wcs.wcs_pix2world(*zip(*pix), 0)))

                if not any(self.wcs.wcs.crval):
                    self.wcs.wcs.crval = sky[0]

                worlds += sky
                pixels += list(zip(*self.wcs.wcs_world2pix(*zip(*sky), 0)))

        (ix0, iy0) = np.argmin(pixels, axis=0)
        (ixx, iyy) = np.argmax(pixels, axis=0)

        self.wcs.wcs.crpix = -pixels[ix0][0], -pixels[iy0][1]

        w = int(pixels[ixx][0] - pixels[ix0][0])
        h = int(pixels[iyy][1] - pixels[iy0][1])

        if w * h > 8e6:
            showerror('Error', 'Image is too big')
            return

        for fg in self.filegroups:
            fg.data = fg.image = np.zeros((h, w))
