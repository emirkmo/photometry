from tkinter import *

from ..scrollableframe import ScrollableFrame

from .image import Image
from .catalog import Catalog
from .solution import Solution

class Settings (ScrollableFrame) :

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.image = Image(self, removeable=False)
        self.catalog = Catalog(self, removeable=False)
        self.solution = Solution(self, removeable=False)

        self.settings = [
                self.image,
                self.catalog,
                self.solution
        ]

        for s in self.settings:
            s.pack(fill=X, side=TOP, pady=5, padx=5)

        self.starmapper = None
