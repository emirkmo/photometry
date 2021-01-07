from matplotlib.figure import Figure

class BlitFigure (Figure) :

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._background = None
        self._artists = []

    def initialize(self):

        self.canvas.mpl_connect('draw_event', self.on_draw)

    def add_artist(self, artist):

        artist.set_animated(True)
        self._artists.append(artist)

    def del_artist(self, artist):

        self._artists.remove(artist)

    def on_draw(self, e):

        self._background = self.canvas.copy_from_bbox(self.bbox)

        for artist in self._artists:
            self.draw_artist(artist)

    def update(self):

        if self._background is None:
            self.on_draw(None)

        self.canvas.restore_region(self._background)

        for artist in self._artists:
            self.draw_artist(artist)

        self.canvas.blit(self.bbox)

        self.canvas.flush_events()
