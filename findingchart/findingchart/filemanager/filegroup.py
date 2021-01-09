from tkinter import *
from tkinter.filedialog import askopenfilenames
from tkinter.messagebox import showerror

import numpy as np

from scipy.interpolate import UnivariateSpline

from astropy.io import fits
from astropy.wcs import WCS

from reproject import reproject_interp

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .file import File

class FileGroup (Frame) :

    def __init__(self, master, title):

        super().__init__(master, highlightbackground='black', highlightthickness=1, padx=5, pady=5)

        self.files = []
        self.image = np.zeros((1, 1))
        self.data, self.ldata = None, dict()

        Label(self, text=title, anchor=W, background='gray', padx=10).pack(fill=X)

        facecolor = self.master.cget('background')
        self.fig = Figure(figsize=(3.6, 2.2), facecolor=facecolor)
        self.fig.subplots_adjust(left=.025, right=.975, bottom=.04, top=.96)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(expand=True, fill=BOTH, side=TOP)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])

        self.curve = type('Curve', (object,), dict())
        self.curve.data = [(0, 0), (1, 1)]
        self.curve.x = np.linspace(0, 1, 100)
        self.curve.f = UnivariateSpline(*zip(*self.curve.data), k=1, s=0, ext=3)
        self.curve.curve, = self.ax.plot(self.curve.x, self.curve.f(self.curve.x), color='black', picker=True)
        self.curve.markers, = self.ax.plot(*zip(*self.curve.data), ls='', color='black', marker='o', ms=10, mfc='white')
        self.curve.marker = None

        self.fig.canvas.mpl_connect('pick_event', self.on_pick_event)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion_notify_event)

        _ = Button(self, text='Add image', background='green', command=self.add_files)
        _.pack(side=BOTTOM, fill=X, expand=True, pady=(5, 2))

        self.fig.canvas.draw()

    def add_files(self):

        for f in askopenfilenames(filetypes=[('FITS', '.fits')]):
            self.add_file(f)

        self.master.register_data()

        if all([len(fg.files) for fg in self.master.filegroups]):

            for fg in self.master.filegroups:
                fg.update_data()
                fg.update_image()

            self.master.update_image()

    def add_file(self, filename):

        path, filename = filename.rsplit('/', 1)

        try:
            with fits.open('%s/%s' % (path, filename)) as hdul:
                data = hdul[0].data
                wcs = WCS(hdul[0].header)
        except:
            showerror('Error', 'Couldn\'t load %s' % filename)
            return

        for fg in self.master.filegroups:
            for f in fg.files:
                f.data_changed = True

        f = File(self, filename, data, wcs)
        self.files.append(f)
        f.pack(fill=X, side=TOP, expand=True)

    def update_data(self):

        weight = 0
        self.data *= 0

        for f in self.files:

            if f.data_changed:
                self.ldata[f], mask = \
                        reproject_interp((f.data, f.wcs), self.master.wcs, self.data.shape)
                self.ldata[f][~mask.astype(bool)] = np.nanmin(self.ldata[f])
                weight += f.weight
                f.data_changed = False

            self.data += self.ldata[f]

        self.data /= weight if weight else 1

        self.update_histogram()

    def update_histogram(self):

        if hasattr(self.curve, 'hist'):
            self.curve.hist.remove()
            del self.curve.hist

        if not len(self.files):
            return

        counts, bins = np.histogram((self.data - self.data.min()) / (self.data - self.data.min()).max(), bins=100)
        counts[0] = counts[-1] = 0
        self.curve.hist = self.ax.hist(bins[:-1], bins, color='silver', weights=counts/counts.max()/1.05)[2]

        self.fig.canvas.draw()

    def update_image(self):

        if not len(self.files):
            self.image = np.zeros((1, 1))
            return

        _min, _max = np.nanmin(self.data), np.nanmax(self.data)
        self.image = (self.data - _min) / np.nanmax(self.data - _min)
        self.image = self.curve.f(self.image)
        self.image[self.image < 0], self.image[self.image > 1] = 0, 1
        self.image = self.image * np.nanmax(self.data - _min) + _min

    def on_motion_notify_event(self, e):

        if not e.button == 1 and \
                not self.curve.marker is None:
            self.curve.marker = None
            self.update_image()
            self.master.update_image()
        if not e.inaxes is self.ax or \
                self.curve.marker is None:
            return

        x, y = min(max(e.xdata, 0), 1), min(max(e.ydata, 0), 1)
        self.curve.data[self.curve.marker] = (x, y)
        self.curve.data.sort(key=lambda c: c[0])
        self.curve.marker = self.curve.data.index((x, y))
        k = min(3, len(self.curve.data) - 1)
        try:
            self.curve.f = UnivariateSpline(*zip(*self.curve.data), k=k, s=0, ext=3)
        except:
            pass

        self.curve.curve.set_data(self.curve.x, self.curve.f(self.curve.x))
        self.curve.markers.set_data(*zip(*self.curve.data))

        self.fig.canvas.draw()

    def on_pick_event(self, e):

        if not e.mouseevent.inaxes is self.ax:
            return

        x, y = e.mouseevent.xdata, e.mouseevent.ydata
        d = np.sum(np.power([x, y] - np.array(self.curve.data), 2), axis=1)
        i = np.argmin(d)

        if d[i] < .002:
            if e.mouseevent.button == 1:
                self.curve.marker = i
            elif e.mouseevent.button == 3 and len(self.curve.data) > 2:
                self.curve.data.pop(i)
                k = min(3, len(self.curve.data) - 1)
                self.curve.f = UnivariateSpline(*zip(*self.curve.data), k=k, s=0, ext=3)
                self.update_image()
                self.master.update_image()
        else:
            if e.mouseevent.button == 1:
                self.curve.data.append((x, y))
                self.curve.data.sort(key=lambda c: c[0])
                self.curve.marker = self.curve.data.index((x, y))
                k = min(3, len(self.curve.data) - 1)
                self.curve.f = UnivariateSpline(*zip(*self.curve.data), k=k, s=0, ext=3)

        self.curve.curve.set_data(self.curve.x, self.curve.f(self.curve.x))
        self.curve.markers.set_data(*zip(*self.curve.data))

        self.fig.canvas.draw()
