import hashlib
import io
import os
import plistlib
import time
from urllib import parse as urlparse
from datetime import date
from time import mktime

from utils import path_insensitive, fix_path
from base_library import Library, Song, Playlist


class ITunesLibrary(Library):

    def __init__(self, media_path, xml_file, media_internal_path, files_only=False):
        self.media_internal_path = media_internal_path
        self.files_only = files_only
        print("Load xml file")
        with open(xml_file, "rb") as f:
            bio = io.BytesIO(f.read())  # gvfs files are not always seekable
            self.il = plistlib.load(bio)
        super(ITunesLibrary, self).__init__(media_path)

    def load_songs(self):
        date_format = "%Y-%m-%d %H:%M:%S"
        songs = []

        print("Validating tracks")
        total = len(self.il['Tracks'])
        for idx, (trackid, attributes) in enumerate(self.il['Tracks'].items()):
            print("\r % 2d%%" % int(100. * idx / total), end="")
            s = Song()
            s.name = attributes.get('Name')
            s.track_id = int(attributes.get('Track ID'))
            s.artist = attributes.get('Artist')
            s.album_artist = attributes.get('Album Artist')
            s.composer = attributes.get('Composer')
            s.album = attributes.get('Album')
            s.genre = attributes.get('Genre')
            s.kind = attributes.get('Kind')
            if attributes.get('Size'):
                s.size = int(attributes.get('Size'))
            s.total_time = attributes.get('Total Time')
            s.track_number = attributes.get('Track Number')
            if attributes.get('Track Count'):
                s.track_count = int(attributes.get('Track Count'))
            if attributes.get('Disc Number'):
                s.disc_number = int(attributes.get('Disc Number'))
            if attributes.get('Disc Count'):
                s.disc_count = int(attributes.get('Disc Count'))
            if attributes.get('Year'):
                s.year = int(attributes.get('Year'))
            if attributes.get('Date Modified'):
                s.date_modified = time.strptime(str(attributes.get('Date Modified')), date_format)
            if attributes.get('Date Added'):
                s.date_added = time.strptime(str(attributes.get('Date Added')), date_format)
            if attributes.get('Bit Rate'):
                s.bit_rate = int(attributes.get('Bit Rate'))
            if attributes.get('Sample Rate'):
                s.sample_rate = int(attributes.get('Sample Rate'))
            s.comments = attributes.get("Comments")
            if attributes.get('Rating'):
                s.rating = int(attributes.get('Rating'))
            s.rating_computed = 'Rating Computed' in attributes
            if attributes.get('Play Count'):
                s.play_count = int(attributes.get('Play Count'))
            if attributes.get('Location'):
                s.location = attributes.get('Location')
                s.location = urlparse.unquote(urlparse.urlparse(attributes.get('Location')).path[1:])
                s.location = s.location  # fixes bug #19
                if self.media_internal_path is None or self.media_path is None:
                    raise Exception("media_internal_path or media_path not set")
                if self.media_internal_path in self.media_path:
                    raise Exception("media_internal_path <%s> incorrect for: %s"
                                    % (self.media_internal_path, s.location))
                if self.media_internal_path not in s.location:
                    print("\r media_internal_path <%s> not in location of media <%s>" %
                          (self.media_internal_path, s.location))
                s.location = path_insensitive(s.location.replace(self.media_internal_path, self.media_path))
            s.compilation = 'Compilation' in attributes
            if attributes.get('Play Date UTC'):
                s.lastplayed = time.strptime(str(attributes.get('Play Date UTC')), date_format)
            if attributes.get('Skip Count'):
                s.skip_count = int(attributes.get('Skip Count'))
            if attributes.get('Skip Date'):
                s.skip_date = time.strptime(str(attributes.get('Skip Date')), date_format)
            if attributes.get('Total Time'):
                s.length = int(attributes.get('Total Time'))
            if attributes.get('Grouping'):
                s.grouping = attributes.get('Grouping')
            if self.files_only is False or attributes.get('Track Type') == 'File':
                songs.append(s)
        print("\r 100%")
        self.add_songs(songs)

    def load_playlists(self):
        print("Load playlists")
        new_playlists = []
        for p in self.il['Playlists']:
            pl = Playlist(p["Name"], p["Playlist Persistent ID"],
                          p["Parent Persistent ID"] if "Parent Persistent ID" in p else None, self)
            track_num = 1
            if 'Playlist Items' in p:
                for track in p['Playlist Items']:
                    track_id = int(track['Track ID'])
                    t = self.songs[track_id]
                    t.playlist_order = track_num
                    track_num += 1
                    pl.tracks.append(t)
            new_playlists.append(pl)
        self.add_playlists(new_playlists)
        self.add_latest()

    def add_latest(self):
        """
        add latest albums to play-lists
        """

        # filter and sort albums
        albums_dict = {}
        for song_id in self.songs:
            song = self.songs[song_id]
            key = (song.album, song.album_artist or song.artist, date.fromtimestamp(mktime(song.date_added)), song.year)
            if key in albums_dict:
                albums_dict[key].append(song)
            else:
                albums_dict[key] = [song]
        albums_list = [i for i in albums_dict.keys() if len(albums_dict[i]) > 3]
        albums_list.sort(key=lambda x: (x[2], x[0]), reverse=True)

        # create play-lists
        new_playlists = []
        tracks = []
        i = 1
        for alb in albums_list[0:99]:
            name = fix_path(("%02d - %s - %s - %s" % (i, alb[3], alb[1], alb[0])).strip().replace(os.path.sep, "_"))
            i += 1
            m = hashlib.md5(name.encode("utf-8")).hexdigest()
            tracks += albums_dict[alb]
            new_playlists.append(Playlist(name, m, 9, self, albums_dict[alb]))

        # add parent
        new_playlists.append(Playlist("Last Added", 9, None, self, tracks))

        # add to library
        self.add_playlists(new_playlists)
