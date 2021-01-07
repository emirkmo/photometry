from tkinter import *

from .scrollableframe import ScrollableFrame

from .starmapper import StarMapper
from .settings import Settings

def main():

    root = Tk()
    root.title('wcsinteractive')
    root.geometry('1300x600')
    root.minsize(800, 100)

    settings = Settings(root, width=300, padx=10, pady=10)
    settings.pack(fill=Y, side=LEFT)

    starmapper = StarMapper(root)
    starmapper.pack(expand=True, fill=BOTH, side=LEFT)

    settings.starmapper = starmapper
    starmapper.settings = settings

    starmapper.initialize()

    root.mainloop()

if __name__ == '__main__':

    main()
