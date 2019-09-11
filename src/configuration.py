# -*- coding: utf-8 -*-
import json
import codecs
import os


class Configuration(object):

    @classmethod
    def load_json_recursive(cls, fn):
        with codecs.open(fn, encoding="utf-8") as f:
            js = json.loads(f.read())
        if "extends" in js:
            base_fn = os.path.join(os.path.dirname(fn), js["extends"])
            base_js = cls.load_json_recursive(base_fn)
            base_js.update(js)
            return base_js
        return js

    def __init__(self, conf_fn):
        js = self.load_json_recursive(conf_fn)

        # Path where actual iTunes Media is stored.
        self.itunes_media_path = js["ITUNES_MEDIA_PATH"]

        # Path that iTunes accesses Media (for example if iTunes runs on VM).
        # By default this should match ITUNES_MEDIA_PATH
        self.itunes_media_db_path = js["ITUNES_MEDIA_DB_PATH"]

        # Path to copy media to
        self.storage_copy_media_path = js["STORAGE_COPY_MEDIA_PATH"]

        # Path path to copy playlist files to
        self.storage_copy_playlist_path = js["STORAGE_COPY_PLAYLIST_PATH"]

        # The iTunes library
        self.itunes_library = str(js["ITUNES_LIBRARY"])

        # Whether to user relative paths in M3U files or not.
        self.relative_paths = js["RELATIVE_PATHS"]

        self.cleanup_media_copy_storage = js["CLEANUP_MEDIA_COPY_STORAGE"]

        # if you got folders in your iTunes Library. If IGNORE_FOLDERS = True, all M3U files will be put directly in
        # STORAGE_COPY_PLAYLIST_PATH. If IGNORE_FOLDERS = False, M3U files will be put in folders,
        # matching the iTunes folders
        self.ignore_folders = js["IGNORE_FOLDERS"]

        # absolute path for MP3 Device to STORAGE_COPY_MEDIA. Only for M3U absolute path creation
        # if RELATED_PATH = False.
        self.storage_m3u_media_path = js["STORAGE_M3U_MEDIA_PATH"]

        # path separator on device
        self.storage_path_separator = js["STORAGE_PATH_SEPARATOR"]

        # latest created by this tool
        self.include = js["INCLUDE"]
        self.exclude = js["EXCLUDE"]

        if self.storage_copy_media_path is None:
            self.storage_copy_media_path = self.itunes_media_path

        if self.storage_m3u_media_path is None:
            self.storage_m3u_media_path = self.storage_copy_media_path

        # self.storage_m3u_media_path = os.path.abspath(os.path.expanduser(self.storage_m3u_media_path))
        self.storage_copy_media_path = os.path.abspath(os.path.expanduser(self.storage_copy_media_path))
        self.storage_copy_playlist_path = os.path.abspath(os.path.expanduser(self.storage_copy_playlist_path))
        self.itunes_media_path = os.path.abspath(os.path.expanduser(self.itunes_media_path))
        # self.itunes_media_db_path = os.path.abspath(os.path.expanduser(self.storage_m3u_media_path))
        while self.itunes_media_db_path[-1] == "/":
            self.itunes_media_db_path = self.itunes_media_db_path[:-1]
        while self.storage_m3u_media_path[-1] == self.storage_path_separator:
            self.storage_m3u_media_path = self.storage_m3u_media_path[:-1]

        if not os.path.exists(self.itunes_media_path):
            raise Exception("library path does not exist: %s" % self.itunes_media_path)
        if not os.path.exists(self.storage_copy_media_path):
            raise Exception("media path does not exist: %s" % self.storage_copy_media_path)
        if not os.path.exists(self.storage_copy_playlist_path):
            raise Exception("playlist path does not exist: %s" % self.storage_copy_playlist_path)