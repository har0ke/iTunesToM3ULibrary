import os
from abc import abstractmethod
from .song import Song
from .playlist import Playlist


class Library(object):

    def __init__(self, media_path):
        self.media_path = media_path
        self.play_lists_by_id = {}
        self.play_lists_by_name = {}
        self.play_list_by_full_name = {}
        self.play_lists = []
        self.songs = {}
        self.load_songs()
        self.load_playlists()

    @abstractmethod
    def load_songs(self):
        """
        load songs into this library and add them via add_songs method
        """
        pass

    @abstractmethod
    def load_playlists(self):
        """
        load playlists into library and add them via add_playlists method
        :return:
        """
        pass

    def add_playlists(self, pls):
        """
        add playlists managed by this library
        :param pls: playlists to add
        """
        for pl in pls:
            self.play_lists_by_id[pl.id] = pl
            if pl.name not in self.play_lists_by_name:
                self.play_lists_by_name[pl.name] = []
            self.play_lists_by_name[pl.name].append(pl)
            self.play_lists.append(pl)
            self.add_songs(pl.tracks)

        for p in self.play_lists:
            self.play_list_by_full_name[self.get_playlist_full_name(p)] = p

    def add_songs(self, songs):
        """
        adds songs to this library to manage
        :param songs: list of songs
        """
        d_songs = {}
        for song in songs:
            d_songs[song.track_id] = song
        self.songs.update(d_songs)

    def get_playlist_full_name(self, pl):
        """
        :param pl: a playlist of this library
        :return: the full hierachy name of this playlist
        """
        def resolve(entry, path=""):
            if entry.parent_id:
                return resolve(self.play_lists_by_id[entry.parent_id], os.path.join(entry.name, path))
            return os.path.join(entry.name, path)
        return resolve(self.play_lists_by_id[pl.id])[:-1]

    def get_playlist_by_name(self, playlistName):
        """
        :param playlistName: name of playlist
        :return: list of playlist, containing playlists with this name
        """
        return self.play_lists_by_name[playlistName]

    def get_play_lists_by_full_name(self, name):
        """
        :param name: full name of playlist
        :return: playlist going by this name
        """
        return self.play_list_by_full_name[name]

    def find_play_lists_by_full_name(self, name):
        """

        :param name: substring
        :return: all playlist's, which's full name contains the substing
        """
        return [self.play_list_by_full_name[k] for k in self.play_list_by_full_name.keys() if name in k]
