class Song(object):

    def __init__(self):
        self.name = None
        self.track_id = None
        self.artist = None
        self.album_artist = None
        self.composer = None
        self.album = None
        self.genre = None
        self.kind = None
        self.size = None
        self.total_time = None
        self.track_number = None
        self.track_count = None
        self.disc_number = None
        self.disc_count = None
        self.year = None
        self.date_modified = None
        self.date_added = None
        self.bit_rate = None
        self.sample_rate = None
        self.comments = None
        self.rating = None
        self.rating_computed = None
        self.album_rating = None
        self.play_count = None
        self.skip_count = None
        self.skip_date = None
        self.location = None
        self.compilation = None
        self.grouping = None
        self.lastplayed = None
        self.length = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Song: %s>" % str(self)
