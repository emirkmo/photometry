from tkinter import *
from tkinter.filedialog import askopenfilename

import numpy as np

from .setting import Setting
from .option import *

CATALOGS = {
        'NOMAD-R' : type('Catalog', (object,), {
                'name': 'NOMAD', 'id': 'I/297/out', 'mag': 'Rmag',
                'ra': 'RAJ2000', 'pm_ra': 'pmRA',
                'dec': 'DEJ2000', 'pm_dec': 'pmDE',
        }),
        'SDSSg' : type('Catalog', (object,), {
                'name': 'sdss', 'id': 'V/147/sdss12', 'mag': 'gmag',
                'ra': 'RA_ICRS', 'pm_ra': 'pmRA',
                'dec': 'DE_ICRS', 'pm_dec': 'pmDE',
        }),
        '2MASS-J' : type('Catalog', (object,), {
                'name': '2MASS', 'id': 'II/246/out', 'mag': 'Jmag',
                'ra': 'RAJ2000',
                'dec': 'DEJ2000', 
        }),
}

IMAGES = [
        'DSS', 'SDSSg', '2MASS-J'
]

class Catalog (Setting) :

    def __init__(self, master, removeable=True):

        super().__init__(master, removeable)

        self.set_title('Catalog')

        self.coordinates = CATALOGS['NOMAD-R']
        self.image = 'DSS'
        self.ra = 0.0
        self.dec = 0.0
        self.radius = 0.25
        self.max_stars = 100

        self.widgets = type('Widgets', (object,), dict())

        coordinates = OptionMenu(self, 'Coordinates', 'NOMAD-R', list(CATALOGS.keys()) + ['Custom'])
        coordinates.command = lambda v: self.set_coordinates(v)
        coordinates.pack(fill=X)

        image = OptionMenu(self, 'Image', self.image, IMAGES + ['None', 'Custom'])
        image.command = lambda v: self.set_image(v)
        image.pack(fill=X)

        self.widgets.ra = Entry(self, 'R.A.', self.ra)
        self.widgets.ra.validate = lambda v: (v >= 0) & (v <= 360)
        self.widgets.ra.command = lambda v: self.set_position(ra=v)
        self.widgets.ra.pack(fill=X)

        self.widgets.dec = Entry(self, 'Dec.', self.dec)
        self.widgets.dec.validate = lambda v: (v >= -180) & (v <= 180)
        self.widgets.dec.command = lambda v: self.set_position(dec=v)
        self.widgets.dec.pack(fill=X)

        self.widgets.radius = Entry(self, 'Radius', self.radius)
        self.widgets.radius.validate = lambda v: (v > 0)
        self.widgets.radius.command = lambda v: self.set_radius(v)
        self.widgets.radius.pack(fill=X)

        max_stars = Entry(self, 'Max. stars', self.max_stars)
        max_stars.validate = lambda v: (v > 0)
        max_stars.command = lambda v: self.set_max_stars(v)
        max_stars.pack(fill=X)

        load_catalog = Button(self, 'Load catalog')
        load_catalog.command = lambda: self.master.starmapper.load_catalog()
        load_catalog.pack(fill=X)

    def set_coordinates(self, v):

        self.coordinates = CATALOGS[v] if v in CATALOGS else v

    def set_image(self, v):

        self.image = v

    def set_position(self, ra=None, dec=None):

        if not ra is None and ra != self.widgets.ra.get():
            self.widgets.ra.set(ra)

        if not dec is None and dec != self.widgets.dec.get():
            self.widgets.dec.set(dec)

        self.ra  = ra  if not ra  is None else self.ra
        self.dec = dec if not dec is None else self.dec

    def set_radius(self, radius):

        if radius != self.widgets.radius.get():
            self.widgets.radius.set(radius)

        self.radius = radius

    def set_max_stars(self, max_stars):

        self.max_stars = max_stars
