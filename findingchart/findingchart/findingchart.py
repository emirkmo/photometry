from tkinter import *

from .filemanager import FileManager
from .fitsviewer import FITSViewer
from .properties import Properties

def main():

    root = Tk()
    root.title('findingchart')
    root.geometry('1300x600')
    root.minsize(800, 100)

    filemanager = FileManager(root, width=400, padx=10, pady=10)
    filemanager.pack(fill=Y, side=LEFT)

    fitsviewer = FITSViewer(root)
    fitsviewer.pack(expand=True, fill=BOTH, side=LEFT)

    properties = Properties(root, width=300, padx=10, pady=10)
    properties.pack(fill=Y, side=RIGHT)

    filemanager.fitsviewer = fitsviewer
    filemanager.properties = properties

    fitsviewer.filemanager = filemanager
    fitsviewer.properties = properties

    properties.filemanager = filemanager
    properties.fitsviewer = fitsviewer

    properties.initialize()

    root.mainloop()
