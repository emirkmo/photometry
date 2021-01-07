from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror

from threading import Event

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import ConnectionPatch
from matplotlib.lines import Line2D

import astropy.units as u

from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.wcs import WCS
from astropy.time import Time
from astropy.coordinates import SkyCoord

from astroquery.vizier import Vizier
from astroquery.skyview import SkyView

from photutils import IRAFStarFinder

from .blitfigure import BlitFigure
from .connection import Connection
from .transform import Transform

Vizier.ROW_LIMIT = -1

class StarMapper (BlitFigure) :

    def __init__(self, *args, **kwargs):

        self.frame = Frame(*args, **kwargs)
        self.frame.pack_propagate(False)

        super().__init__()

        self.canvas = FigureCanvasTkAgg(self, master=self.frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=BOTH, side=TOP)

        self.subplots_adjust(left=.025, right=.975, bottom=.15, top=.90, wspace=.05)

        self.canvas.mpl_connect('button_press_event', self.on_button_press_event)
        self.canvas.mpl_connect('button_release_event', self.on_button_release_event)
        self.canvas.mpl_connect('scroll_event', self.on_scroll_event)

        self.canvas.mpl_connect('motion_notify_event', self.on_motion_notify_event)
        self.canvas.mpl_connect('pick_event', self.on_pick_event)

        self.hdu, self.points = None, []
        self.connection, self.connections = None, []
        self.ax, self.axl, self.axr = None, None, None

        self.transform = Transform(self.frame)
        self.transform.on_mirror = lambda m: (self.transform_data(), self.transform_points(), self.transform_connections(), self.canvas.draw())
        self.transform.on_rotation = lambda r: (self.transform_data(), self.transform_points(), self.transform_connections(), self.canvas.draw())
        self.transform.place(anchor=S, relwidth=.7, height=20, relx=.5, rely=.95)

        self.timer = type('Timers', (object,), dict(
                clim = self.canvas.new_timer(interval=250),
                zoom = self.canvas.new_timer(interval=100),
        ))

        self.timer.clim.single_shot = True
        self.timer.clim.event = Event()

        self.timer.zoom.single_shot = True
        self.timer.zoom.event = Event()
        self.timer.zoom.add_callback(self.timer.zoom.event.clear)

        self.settings = None

    def clear_connections(self):

        while len(self.connections):

            self.connections.pop().remove()

    def open_image(self):

        fn = askopenfilename(filetypes=[('FITS', '.fits')])

        if not fn:
            return

        try:
            with fits.open(fn) as hdul:
                self.hdu = hdul[0].copy()
        except:
            showerror('Error', 'Failed to open image %s' % fn)
            return

        self.hdu.wcs = WCS(self.hdu.header)
        h, w = self.hdu.data.shape

        self.clear_connections()

        if list(self.hdu.wcs.wcs.ctype) != ['', '']:

            [(ra, dec)] = self.hdu.wcs.wcs_pix2world([(w/2, h/2)], 0)
            self.settings.catalog.set_position(ra, dec)

            c = SkyCoord(self.hdu.wcs.wcs_pix2world([(0, 0), (w, h)], 0), unit=('deg', 'deg'))
            self.settings.catalog.set_radius(c[0].separation(c[1]).value/2)

            scale = np.sqrt(np.power(self.hdu.wcs.wcs.pc, 2).sum() / 2) * 60 * 60
            self.settings.image.set_scale(scale)

            self.transform.set_from_matrix(self.hdu.wcs.pixel_scale_matrix)

        if 'seeing' in self.hdu.header:

            self.settings.image.set_seeing(self.hdu.header['seeing'])

        if np.isfinite(self.hdu.wcs.wcs.mjdobs):

            year = Time(self.hdu.wcs.wcs.mjdobs, format='mjd').jyear
            self.settings.image.set_obs_year(year)

        threshold = 5 * sigma_clipped_stats(self.hdu.data)[2]
        self.settings.image.set_threshold(threshold)

        if self.axl:
            self.axl.remove()

        self.axl = self.add_subplot(121)
        self.axl.set_axis_off()

        clim = np.nanquantile(self.hdu.data, (.01, .99))
        self.axl.image = self.axl.imshow([[0]], origin='lower', cmap='gray_r', clim=clim)
        self.axl.wcs = self.hdu.wcs
        self.axl.artist = self.axl.scatter([], [], c=[], s=200, edgecolors=(1, 0, 0, .25), picker=True)

        self.axl.artist.point = self.axl.scatter([], [], c=[], s=200, edgecolors=(.25, .25, 1))
        self.add_artist(self.axl.artist.point)

        self.transform_data()

        self.settings.image.widgets.find_stars.set_disabled(False)
        self.settings.solution.set_disabled(False)

        self.canvas.draw()

    def find_stars(self):

        fwhm = self.settings.image.seeing / self.settings.image.scale
        threshold = self.settings.image.threshold
        background = sigma_clipped_stats(self.hdu.data)[1]
        max_stars = self.settings.image.max_stars

        finder = IRAFStarFinder(threshold, fwhm)
        stars = finder(self.hdu.data - np.median(self.hdu.data))

        if not stars:
            showerror('Error', 'Failed to find stars')
            return

        i = np.argsort(stars['mag'])[:max_stars]
        self.points = list(zip(stars['xcentroid'][i], stars['ycentroid'][i]))

        self.transform_points()

        self.canvas.draw()

    def transform_data(self):

        if not self.axl:
            return

        data = self.transform.transform_data(self.hdu.data)
        self.axl.image.set_data(data)
        self.axl.image.set_extent([0, data.shape[1], 0, data.shape[0]])

        self.axl.set_xlim(0, data.shape[1])
        self.axl.set_ylim(0, data.shape[0])

    def transform_points(self):

        if not self.axl:
            return

        shape_in, shape_out = self.hdu.data.shape, self.axl.image.get_array().shape
        points = self.transform.transform_points(self.points, shape_in, shape_out)
        self.axl.artist.set_offsets(points)

    def transform_connections(self):

        if not self.axl:
            return

        shape_in, shape_out = self.hdu.data.shape, self.axl.image.get_array().shape

        for connection in self.connections:

            point = connection.get_xy()[self.axl]
            point = self.transform.transform_points([point], shape_in, shape_out)[0]

            i = [connection.con.axesA, connection.con.axesB].index(self.axl)
            setattr(connection.con, 'xy2' if i else 'xy1', point)
            connection.scat[i].set_offsets([point])

    def load_catalog(self):

        coordinates = self.settings.catalog.coordinates
        image = self.settings.catalog.image
        obs_year = self.settings.image.obs_year
        ra, dec = self.settings.catalog.ra, self.settings.catalog.dec
        radius = self.settings.catalog.radius
        max_stars = self.settings.catalog.max_stars

        coordinate, radius = SkyCoord(ra * u.deg, dec * u.deg), radius * u.deg

        if image == 'None':

            data, wcs = np.zeros((2,2)), WCS()
            wcs.wcs.cdelt = -radius.value, radius.value
            wcs.wcs.crpix = 2, 2
            wcs.wcs.crval = ra, dec

        elif image == 'Custom':

            fn = askopenfilename(title='Image', filetypes=[('FITS', '.fits')])

            if not fn:
                return

            try:
                with fits.open(fn) as hdul:
                    data, wcs = hdul[0].data, WCS(hdul[0].header)
            except:
                showerror('Error', 'Failed to open catalog image %s' % fn)
                return

        else:

            try:
                with SkyView.get_images(position=coordinate, survey=image, radius=radius)[0] as hdul:
                    data, wcs = hdul[0].data, WCS(hdul[0].header)
            except:
                showerror('Error', 'Failed to get catalog image')
                return

        if coordinates == 'Custom':

            fn = askopenfilename(title='Catalog')

            if not fn:
                return

            try:
                c = np.loadtxt(fn, unpack=True)
            except:
                showerror('Error', 'Failed to open catalog coordinates %s' % fn)
                return

            try:
                c[0][0]
            except:
                c = [np.array([r]) for r in c]

            if len(c) < 2:
                return

            if len(c) >= 5:
                ra = (c[0] * u.deg + (obs_year - 2000) * c[3] * u.marcsec).value
                dec = (c[1] * u.deg + (obs_year - 2000) * c[4] * u.marcsec).value

            x, y = map(np.array, zip(*wcs.wcs_world2pix(list(zip(ra, dec)), 0)))
            i = np.where((x >= 0) & (x <= data.shape[1]) & (y >= 0) & (y <= data.shape[0]))
            x, y = x[i], y[i]

            if len(c) > 2:
                mag = c[2]
                i = np.argsort(mag)
                x, y = x[i], y[i]

            catalog_xy = list(zip(x[:max_stars], y[:max_stars]))

        else:

            try:
                c = Vizier.query_region(coordinate, radius=radius, catalog=coordinates.name)[coordinates.id]
            except:
                showerror('Error', 'Failed to get catalog coordinates')
                return

            ra, dec = c[coordinates.ra], c[coordinates.dec]
            if hasattr(coordinates, 'pm_ra'):
                ra = c[coordinates.ra] + (obs_year - 2000) * c[coordinates.pm_ra] * u.marcsec
            if hasattr(coordinates, 'pm_dec'):
                dec = c[coordinates.dec] + (obs_year - 2000) * c[coordinates.pm_dec] * u.marcsec

            x, y = map(np.array, zip(*wcs.wcs_world2pix(list(zip(ra, dec)), 0)))
            i = np.where((x < 0) | (x > data.shape[1]) | (y < 0) | (y > data.shape[0]))
            c.remove_rows(i); c.sort(coordinates.mag)
            catalog = list(zip(c[coordinates.ra][:max_stars], c[coordinates.dec][:max_stars]))
            catalog_xy = wcs.wcs_world2pix(catalog, 0)

        if self.axr:

            if np.all(data == self.axr.image.get_array().data):

                self.axr.artist.set_offsets(catalog_xy)
                self.canvas.draw()

                return

            self.clear_connections()
            self.axr.remove()

        self.axr = self.add_subplot(122)
        self.axr.set_axis_off()

        clim = np.nanquantile(data, (.01, .99))
        self.axr.image = self.axr.imshow(data, cmap='gray_r', clim=clim)
        self.axr.wcs = wcs
        self.axr.artist = self.axr.scatter(*zip(*catalog_xy), c=[], s=200, edgecolors=(1, 0, 0, .25), picker=True)

        self.axr.artist.point = self.axr.scatter([], [], c=[], s=200, edgecolors=(.25, .25, 1))
        self.add_artist(self.axr.artist.point)

        self.axr.set_xlim(0, data.shape[1])
        self.axr.set_ylim(0, data.shape[0])

        self.canvas.draw()

    def on_pick_event(self, e):

        if hasattr(e.artist, 'parent') and \
                type(e.artist.parent) is Connection:

            connection = e.artist.parent

            if e.mouseevent.button == 3 and \
                    connection in self.connections and \
                    not self.ax and \
                    not self.timer.clim.event.is_set():

                self.connections.remove(connection)
                connection.remove()

            else:

                connection.set_color((.25, .25, 1))

        else:

            try:

                x, y = e.mouseevent.xdata, e.mouseevent.ydata
                stars = e.artist.get_offsets()
                i = e.ind[np.argmin([(x-xi)**2 + (y-yi)**2 for xi, yi in stars[e.ind]])]

            except:

                return

            if not self.connection or \
                    not self.connection.ax0 is e.mouseevent.inaxes:

                e.artist.point.set_offsets(stars[i])

            if e.mouseevent.button == 1 and \
                    not self.connection:

                self.connection = Connection(self, e.mouseevent.inaxes, *stars[i])

                if e.mouseevent.inaxes is self.axl:
                    self.connection.x0, self.connection.y0 = self.points[i]

            elif not e.mouseevent.button and \
                    self.connection and \
                    e.mouseevent.inaxes != self.connection.ax0:

                self.connection.set_xy(e.mouseevent.inaxes, *stars[i])
                self.connection.define()

                if e.mouseevent.inaxes is self.axl:
                    self.connection.xx, self.connection.yy = self.points[i]

                self.connections.append(self.connection)
                self.connection = None

                self.transform_connections()

                self.update()

    def on_motion_notify_event(self, e):

        for connection in self.connections:
            connection.set_color((.5, 1, .5))

        if self.axl:
            self.axl.artist.point.set_offsets([[],[]])
        if self.axr:
            self.axr.artist.point.set_offsets([[],[]])

        self.canvas.pick(e)

        if self.connection:

            if e.button == 1:

                self.connection.set_xy(None, e.x, e.y)

            else:

                self.connection.remove()
                self.connection = None

        elif self.ax and e.button == 3:

            [(x, y)] = self.transFigure.inverted().transform([(e.x, e.y)])
            p, w = min(max(x, 0), 1), min(max(np.log10(9*y + 1), 0), 1)

            q = max(p-w/2, 0), min(p+w/2, 1)
            try:
                clim = np.nanquantile(self.ax.image.get_array(), q)
            except:
                return
            self.ax.image.set_clim(clim)

            self.canvas.draw()

            return

        self.update()

    def on_button_press_event(self, e):

        if not e.inaxes:
            return

        if e.button == 2:

            h, w = e.inaxes.image.get_array().shape
            if 0 > e.xdata or e.xdata > w or 0 > e.ydata or e.ydata > h:
                return

            (x0, xx), (y0, yy) = e.inaxes.get_xlim(), e.inaxes.get_ylim()
            dx, dy = xx - x0, yy - y0

            x0, xx = e.xdata + np.array([-dx, dx])/2
            y0, yy = e.ydata + np.array([-dy, dy])/2

            if x0 < 0:
                x0, xx = 0, xx - x0
            elif xx > w:
                x0, xx = x0 - xx + w, w

            if y0 < 0:
                y0, yy = 0, yy - y0
            elif yy > h:
                y0, yy = y0 - yy + h, h

            e.inaxes.set_xlim((x0, xx))
            e.inaxes.set_ylim((y0, yy))

            self.canvas.draw()

        elif e.button == 3:

            for callback in self.timer.clim.callbacks:
                self.timer.clim.remove_callback(callback[0])
            self.timer.clim.add_callback(lambda ax: setattr(self, 'ax', ax), e.inaxes)

            self.timer.clim.event.set()
            self.timer.clim.start()

    def on_button_release_event(self, e):

        if self.connection:

            self.canvas.pick(e)
            return

        self.timer.clim.stop()
        self.timer.clim.event.clear()

        self.ax = None

    def on_scroll_event(self, e):

        if not e.inaxes or \
                self.timer.zoom.event.is_set():
            return

        self.timer.zoom.event.set()

        (x0, xx), (y0, yy) = e.inaxes.get_xlim(), e.inaxes.get_ylim()
        x, y = (xx + x0) / 2, (yy + y0) / 2
        h, w = e.inaxes.image.get_array().shape

        d = (xx - x0) if w > h else (yy - y0)
        d *= (1 - 0.2 * e.step) / 2

        x0, xx = max(x-d, 0), min(x+d, w)
        y0, yy = max(y-d, 0), min(y+d, h)

        e.inaxes.set_xlim((x0, xx))
        e.inaxes.set_ylim((y0, yy))

        self.canvas.draw()

        self.timer.zoom.start()

    def pack(self, *args, **kwargs):

        self.frame.pack(*args, **kwargs)
