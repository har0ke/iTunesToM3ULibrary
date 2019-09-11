import os
import json

from utils import fix_path


class Action(object):

    def execute(self):
        pass

    def get_change_info(self):
        pass

    def __repr__(self):
        return "Change: %s" % self.get_change_info()


class SynchronisationAction(Action):

    def __init__(self, sync):
        print("Initialize %s" % self.__class__.__name__)
        assert(isinstance(sync, LibrarySynchronisation))
        self.sync_obj = sync


class CopyMediaAction(SynchronisationAction):

    def __init__(self, *args, **kwargs):
        super(CopyMediaAction, self).__init__(*args, **kwargs)
        if self.sync_obj.library.media_path == self.sync_obj.storage.media_path:
            self.tracks_to_create = set([])
        else:
            self.tracks_to_create = set(self.sync_obj.get_copy_mapping().keys())\
                .difference(set(self.sync_obj.explore_media()))

    def execute(self):
        size = float(len(self.tracks_to_create))
        count = 0.0
        copy_mapping = self.sync_obj.get_copy_mapping()
        for t in self.tracks_to_create:
            if not t.startswith(self.sync_obj.storage.media_path):
                raise Exception("Invalid Track path: \n" + "\n".join((t, self.sync_obj.storage.media_path)))
            count += 1.0
            print("%.2F%% Copy Track: %s" % (count / size * 100, t))
            self.sync_obj.storage.copy(copy_mapping[t].location, t)

    def get_change_info(self):
        return "Tracks to add: " + json.dumps(list(self.tracks_to_create), indent=4)


class RemoveEmptyDirs(SynchronisationAction):

    @staticmethod
    def find_empty_dirs(root_dir='.'):
        """
        fetches all empty dirs in storage
        :param root_dir: dir do recusively search for empty dis
        :return: iterator over empty dir paths
        """
        for dirpath, dirs, files in os.walk(root_dir):
            if not dirs and not files:
                yield dirpath

    def execute(self):
        print("Remove Empty Dirs...")
        for i in self.find_empty_dirs(self.sync_obj.storage.media_path):
            os.removedirs(i)
        for i in self.find_empty_dirs(self.sync_obj.storage.playlist_path):
            os.removedirs(i)

    def get_change_info(self):
        return "Remove empty dirs."


class RemoveNotWantedMedia(SynchronisationAction):

    def __init__(self, *args, **kwargs):
        super(RemoveNotWantedMedia, self).__init__(*args, **kwargs)
        self.tracks_to_delete = set(self.sync_obj.explore_media())\
            .difference(set(self.sync_obj.get_copy_mapping().keys()))

    def execute(self):
        for t in self.tracks_to_delete:
            if not t.startswith(self.sync_obj.storage.media_path):
                raise Exception("Track path '%s' does not start with '%s'" % (t, self.sync_obj.storage.media_path))
            print("Remove Track: ", t)
            os.remove(t)

    def get_change_info(self):
        return "Tracks to delete: " + json.dumps(list(self.tracks_to_delete), indent=4)


class RemoveNotWantedPlaylist(SynchronisationAction):

    def __init__(self, *args, **kwargs):
        super(RemoveNotWantedPlaylist, self).__init__(*args, **kwargs)
        self.playlists_to_delete = (set(self.sync_obj.explore_playlists())
                                    .difference(set(self.sync_obj.get_playlist_mapping().keys())))

    def execute(self):
        for p in self.playlists_to_delete:
            print("Remove Playlist: ", p)
            os.remove(p)

    def get_change_info(self):
        return "Playlist to delete: " + json.dumps(list(self.playlists_to_delete), indent=4)


class CopyPlaylists(SynchronisationAction):
    def __init__(self, sync, update_playlists):
        super(CopyPlaylists, self).__init__(sync)
        self.update_playlists = update_playlists
        self.playlists_to_create = set(self.sync_obj.get_playlist_mapping().keys())\
            .difference(set(self.sync_obj.explore_playlists()))

    def execute(self):
        mapping = self.sync_obj.get_playlist_mapping()
        for p in (mapping.keys() if self.update_playlists else self.playlists_to_create):
            content = mapping[p].get_m3u_content(self.sync_obj.library.media_path, self.sync_obj.storage)
            if not self.sync_obj.storage.content_equals(p, content):
                print("Updated Playlist: ", p)
                self.sync_obj.storage.save(p, content)

    def get_change_info(self):
        return ("Playlist to create: %s\n All Playlists will be updated."
                % json.dumps(list(self.playlists_to_create), indent=4))


class LibrarySynchronisation(object):
    """
    Synchronises Library to storage
    """

    def __init__(self, library, storage):
        """
        :param library: library to synchronise
        :param storage: storagee to synchronise to
        """
        self.library = library
        self.storage = storage
        self._playlists = set([])
        self._tracks = set([])

    def add(self, playlists=None, tracks=None):
        """
        add data that should be in storage
        :param playlists: playlists
        :param tracks: tracks
        :return:
        """
        if playlists:
            self._playlists = self._playlists.union(playlists)
            for playlist in playlists:
                self._tracks = self._tracks.union(playlist.tracks)
        if tracks:
            self._tracks = self._tracks.union(tracks)

    @property
    def tracks(self):
        return self._tracks or [self.library.songs[k] for k in self.library.songs]

    @property
    def playlists(self):
        return self._playlists or self.library.play_lists

    def explore_media(self):
        """
        gather all media files
        :return: (media_files, playlist_files)
        """
        audio = ["3gp", "aa", "aac", "aax", "act", "aiff", "amr", "ape", "au", "awb", "dct", "dss", "dvf", "flac",
                 "gsm", "iklax", "ivs", "m4a", "m4b", "m4p", "mmf", "mp3", "mpc", "msv", "ogg", "oga", "mogg", "opus",
                 "ra", "rm", "raw", "sln", "tta", "vox", "wav", "wma", "wv", "webm"]
        media_files = []
        for dirpath, dirnames, filenames in os.walk(self.storage.media_path):
            media_files += [os.path.join(dirpath, filename)
                            for filename in filenames
                            if filename.lower().endswith(tuple(audio))]
        return media_files

    def explore_playlists(self):
        """
        gather all media files
        :return: (media_files, playlist_files)
        """
        playlist_files = []
        for dirpath, dirnames, filenames in os.walk(self.storage.playlist_path):
            playlist_files += [os.path.join(dirpath, filename) for filename in filenames if filename.endswith("m3u")]
        return playlist_files

    def sync(self, update_playlists=True, remove_other_files=True):
        if os.path.abspath(self.storage.media_path) == os.path.abspath(self.library.media_path) and remove_other_files:
            raise Exception("Removing files in original library is not allowed.")

        actions = [
            CopyMediaAction(self),
            CopyPlaylists(self, update_playlists),
            RemoveNotWantedPlaylist(self)
        ]

        if remove_other_files:
            actions += [
                RemoveNotWantedMedia(self),
                RemoveEmptyDirs(self)
            ]

        for action in actions:
            print(action.__class__.__name__)
            print(action)

        value = ""
        while value != "y":
            value = input("Continue with changes? [y/N]: ")
            if value == "n":
                print("Cancel")
                exit(0)

        for action in actions:
            print(action.__class__)
            action.execute()

        print("DONE.")

    def get_copy_mapping(self):
        """
        generate mapping, where tracks should be moved
        :return: dict
        """
        tracks = set(self.tracks)
        mapping = {}
        for t in tracks:
            if t.location:
                mapping[fix_path(self.translate_media_path(t.location))] = t
        return mapping

    def translate_media_path(self, path):
        return fix_path(path.replace(self.library.media_path, self.storage.media_path))

    def get_playlist_mapping(self):
        """
        generate mapping, where playlists should be moved
        :return: dict
        """
        playlists = set(self.playlists)
        mapping = {}
        for p in playlists:
            if self.storage.ignore_folders:
                path = os.path.join(self.storage.playlist_path,
                                    self.library.get_playlist_full_name(p).replace(os.sep, "#") + ".m3u")
            else:
                path = os.path.join(self.storage.playlist_path, self.library.get_playlist_full_name(p) + ".m3u")
            mapping[fix_path(path)] = p
        return mapping
