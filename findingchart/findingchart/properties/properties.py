from tkinter import *

from ..scrollableframe import ScrollableFrame

from .imagedata import ImageData
from .gridlines import GridLines
from .inset import Inset
from .compass import Compass
from .scale import Scale

from .marker import Marker
from .text import Text
from .crosshair import Crosshair

class Properties (ScrollableFrame) :

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.inset = Inset(self)

        self.properties = [
                ImageData(self),
                GridLines(self),
                self.inset,
                Compass(self),
                Scale(self)
        ]

        for p in self.properties:
            p.pack(fill=X, side=TOP, pady=5, padx=5)

        self.fitsviewer = None
        self.filemanager = None

        value, options = StringVar(), ['Marker', 'Text', 'Crosshair']
        value.set('Add property')
        _ = OptionMenu(self, value, *options, command=lambda v: [
                self.add_property(v),
                value.set('Add property')
        ])
        _.config(background='green')
        _.pack(side=BOTTOM, fill=X, expand=True, pady=10, padx=5)

    def initialize(self):

        for p in self.properties:
            if hasattr(p, 'initialize'):
                p.initialize()

    def add_property(self, name):

        _property = {
                'Marker' : Marker,
                'Text' : Text,
                'Crosshair' : Crosshair,
        }.get(name, lambda *_: None)(self)

        if not _property:
            return

        self.properties.append(_property)
        _property.pack(fill=X, side=TOP, pady=5, padx=5)
