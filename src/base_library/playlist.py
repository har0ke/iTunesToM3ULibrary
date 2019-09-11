import copy
import itertools
import os

from utils import fix_path


class Playlist(object):

    def __init__(self, name, id, parent_id, library, tracks=None):
        self.name = name
        self.tracks = tracks or []
        self.id = id
        self.parent_id = parent_id
        self.library = library

    def get_m3u_content(self, media_path, storage):
        device_media_path_list = storage.device_media_path.split(storage.storage_path_separator)
        def is_not_empty_string(s):
            return s != ''
        def c_path(path):
            if storage.use_related_paths:
                rel_p = storage.storage_path_separator.join(["."] + [".." for i in range(len(self.library.get_playlist_full_name(self).split(os.sep)) - 1)])
                rel_p_to_m = os.path.relpath(storage.media_path, storage.playlist_path)
                if storage.ignore_folders:
                    return storage.storage_path_separator.join([rel_p_to_m, path.replace(media_path, "")])
                else:
                    return storage.storage_path_separator.join([rel_p, storage.storage_path_separator.join([rel_p_to_m, path.replace(media_path, "")])])
            return storage.storage_path_separator.join(filter(is_not_empty_string,
                    itertools.chain(device_media_path_list + fix_path(path).replace(media_path, "").split(os.sep))))
        return "\n".join([c_path(t.location) for t in self.sorted_tracks if t.location])

    @property
    def sorted_tracks(self):
        tracks = copy.copy(self.tracks)
        tracks.sort(key=lambda a: (a.track_number if a.track_number is not None else 5))
        return tracks

    def __repr__(self):
        return u"<Playlist: %s>" % str(self)

    def __str__(self):
        return self.library.get_playlist_hierarchy(self)