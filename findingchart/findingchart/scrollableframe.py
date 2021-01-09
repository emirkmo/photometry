from tkinter import *

class ScrollableFrame (Frame) :

    def __init__(self, *args, **kwargs):

        self.parent = Frame(*args, **kwargs)
        self.canvas = Canvas(self.parent, highlightthickness=0)
        self.scrollbar = Scrollbar(self.parent, command=lambda *e: (
            self.canvas.yview(*e),
            self.canvas.yview('moveto', self.canvas.yview()[0])
        ))

        super().__init__(self.canvas)

        canvas_frame = self.canvas.create_window((0, 0), window=self, anchor=N+W)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.bind('<Configure>', lambda e:
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )

        self.canvas.bind('<Configure>', lambda e:
            self.canvas.itemconfig(canvas_frame, width=e.width)
        )

        self.parent.pack_propagate(False)

        self.scrollbar.pack(fill=Y, side=RIGHT)

        self.canvas.pack(expand=True, fill=BOTH, side=LEFT)

    def pack(self, *args, **kwargs):

        self.parent.pack(*args, **kwargs)
