from tkinter import *

from tkinter import Button as tkButton
from tkinter import OptionMenu as tkOptionMenu
from tkinter import Checkbutton as tkCheckBox
from tkinter import Entry as tkEntry

class Button (Frame) :

    def __init__(self, master, text):

        super().__init__(master)

        self.variable = tkButton(self, text=text, command=self._command)
        self.variable['pady'] = 2
        self.variable.pack(fill=X)

    def set_disabled(self, state):

        self.variable['state'] = DISABLED if state else NORMAL

    def _command(self):

        return self.command()

    def command(self):

        return

class OptionMenu (Frame) :

    def __init__(self, master, text, value, options):

        super().__init__(master)

        Label(self, text=text).pack(side=LEFT)

        _ = StringVar(); _.set(value)
        self.variable = tkOptionMenu(self, _, *options, command=self._command)
        self.variable['width'] = 11
        self.variable['pady'] = 2
        self.variable.pack(side=RIGHT, fill=X)

        self.value = value

    def _command(self, e):

        v = e

        if self.value == v:
            return
        else:
            self.value = v

        return self.command(v)

    def command(self, v):

        return

class CheckBox (Frame) :

    def __init__(self, master, text, value):

        super().__init__(master)

        Label(self, text=text).pack(side=LEFT)

        self.variable = tkCheckBox(self, command=self._command)
        self.variable.var = IntVar(value=value)
        self.variable.config(var=self.variable.var)
        self.variable.pack(side=RIGHT, fill=X)

        self.value = self.variable.var.get()

    def _command(self):

        v = self.variable.var.get()

        if self.value == v:
            return
        else:
            self.value = v

        return self.command(v)

    def command(self, v):

        return

class Entry (Frame) :

    def __init__(self, master, text, value):

        super().__init__(master)

        Label(self, text=text).pack(side=LEFT)
        self.dtype = type(value)

        self.variable = tkEntry(self, width=16)
        self.variable.insert(0, self.dtype(value))
        self.variable.bind('<KeyRelease>', self._command)
        self.variable.pack(side=RIGHT, fill=X)

        self.value = self.variable.get()

    def set(self, v):

        self.variable.delete(0, END)
        self.variable.insert(0, v)

        self.value = v

    def get(self):

        return self.value

    def _command(self, *a):

        v = self.variable.get()

        try:
            v = self.dtype(v)
            if not self.validate(v):
                raise Exception
        except:
            self.variable['background'] = 'red'
            return
        else:
            self.variable['background'] = 'white'

        if self.value == v:
            return
        else:
            self.value = v

        return self.command(v)

    def validate(self, v):

        return True

    def command(self, v):

        return
