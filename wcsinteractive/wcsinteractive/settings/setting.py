from tkinter import *

class Setting (Frame) :

    def __init__(self, master, removeable=True, show=True):

        self.container = Frame(master, highlightbackground='black', highlightthickness=1, padx=5, pady=5)

        super().__init__(self.container)

        self.master = master

        titleframe = Frame(self.container, background='gray', cursor='hand2')
        self.point = Label(titleframe, text='\u25b6', font=(None, 7), anchor=CENTER, background='gray', width=2)
        self.title = Label(titleframe, text='Property', anchor=W, background='gray')

        titleframe.bind('<Button-1>', lambda e: self.toggle())
        self.point.bind('<Button-1>', lambda e: self.toggle())
        self.title.bind('<Button-1>', lambda e: self.toggle())

        if removeable:
            _ = Button(titleframe, text='X', font=(None, 8), width=0, padx=3, pady=0, background='red', command=self._remove)
            _.pack(side=RIGHT, padx=(0, 1))
            

        self.point.pack(side=LEFT, padx=(5, 0))
        self.title.pack(side=LEFT)
        titleframe.pack(fill=X)

        if show:
            self.toggle()

    def toggle(self):

        try:
            self.pack_info()
        except:
            self.point['text'] = '\u25bc'
            super().pack(fill=X, pady=(5, 0))
        else:
            self.point['text'] = '\u25b6'
            self.pack_forget()

    def set_title(self, title):

        self.title['text'] = title

    def pack(self, *args, **kwargs):

        self.container.pack(*args, **kwargs)

    def _remove(self):

        self.master.properties.remove(self)
        self.remove()

        self.container.pack_forget()
        self.container.destroy()

    def remove(self):

        return
