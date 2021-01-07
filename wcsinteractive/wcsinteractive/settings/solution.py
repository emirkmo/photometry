from tkinter import *
from tkinter.filedialog import asksaveasfilename

import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord

from scipy.optimize import minimize

from .setting import Setting
from .option import *

class Solution (Setting) :

    def __init__(self, master, removeable=True):

        super().__init__(master, removeable)

        self.set_title('Solution')

        self.widgets = type('Widgets', (object,), dict())

        self.widgets.show = Button(self, 'Show')
        self.widgets.show.command = self.show_solution
        self.widgets.show.set_disabled(True)
        self.widgets.show.pack(fill=X)

        self.widgets.save = Button(self, 'Save')
        self.widgets.save.command = self.save_solution
        self.widgets.save.set_disabled(True)
        self.widgets.save.pack(fill=X)

    def set_disabled(self, state):

        self.widgets.show.set_disabled(state)
        self.widgets.save.set_disabled(state)

    def solve(self):

        starmapper = self.master.starmapper

        connections = [c.get_xy() for c in starmapper.connections]

        if not len(connections):
            return starmapper.hdu.wcs

        wcs = WCS()

        xy = np.array([c[starmapper.axl] for c in connections])
        rd = starmapper.axr.wcs.wcs_pix2world([c[starmapper.axr] for c in connections], 0)

        m = [-1, 1][starmapper.transform.mirror]
        rot = lambda t: np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]).dot(np.diag([m,1]))

        if len(connections) > 1:

            a, b = xy - xy.mean(axis=0), rd - rd.mean(axis=0)
            b[:,0] *= np.cos(np.deg2rad(rd[:,1]))

            if len(connections) > 2:

                wcs.wcs.pc = np.linalg.lstsq(a, b, rcond=None)[0].T

            else:

                c = SkyCoord(rd, unit=('deg', 'deg'))
                s0 = c[0].separation(c[1]).value / np.sqrt(np.power(np.diff(xy, axis=0)[0], 2).sum())

                t0 = np.deg2rad(starmapper.transform.rotation)

                chi2 = lambda x: np.power(a.dot(x[1]*rot(x[0]).T) - b, 2).sum()
                theta, scale = minimize(chi2, [t0, s0]).x

                wcs.wcs.pc = scale * rot(theta)

        elif len(connections) == 1:

            theta = np.deg2rad(starmapper.transform.rotation)
            scale = self.master.image.scale / 60 / 60

            wcs.wcs.pc = scale * rot(theta)

        wcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']

        wcs.wcs.crpix = xy.mean(axis=0) + 1
        wcs.wcs.crval = rd.mean(axis=0)

        return wcs

    def show_solution(self):

        starmapper = self.master.starmapper

        wcs = self.solve()

        data = starmapper.hdu.data
        clim = starmapper.axl.image.get_clim()

        fig = plt.figure()
        ax = fig.add_subplot(111, projection=wcs)

        ax.imshow(data, cmap='gray_r', clim=clim)

        if starmapper.axr:

            xy = starmapper.axr.artist.get_offsets()
            if len(xy):
                rd = starmapper.axr.wcs.wcs_pix2world(xy, 0)
                x, y = map(np.array, zip(*wcs.wcs_world2pix(rd, 0)))
                i = np.where((x >= 0) & (x <= data.shape[1]) & (y >= 0) & (y <= data.shape[0]))
                x, y = x[i], y[i]
            else:
                x, y = [], []
            ax.scatter(x, y, c=[], s=200, edgecolors=(1, 0, 0, .25))

            xy = [c.get_xy()[starmapper.axr] for c in starmapper.connections]
            if len(xy):
                rd = starmapper.axr.wcs.wcs_pix2world(xy, 0)
                x, y = zip(*wcs.wcs_world2pix(rd, 0))
            else:
                x, y = [], []
            ax.scatter(x, y, c=[], s=200, linewidth=1.5, edgecolors=(.5, 1, .5))

        ax.grid(True)
        plt.show()

    def save_solution(self):

        data = self.master.starmapper.hdu.data
        head = self.master.starmapper.hdu.header.copy()

        wcs = self.solve()
        head.update(wcs.to_header())

        fn = asksaveasfilename(
                title='Save new FITS file',
                filetypes=[('FITS', '.fits')],
                defaultextension='.fits'
        )
        if not fn:
            return

        hdu = fits.PrimaryHDU(data, head)
        hdu.writeto(fn, overwrite=True)
