import codecs
import errno
import os
import shutil
import subprocess


class M3UStorage(object):
    """
    holds data of storage to copy library to
    """

    def __init__(self, media_path, playlist_path, use_related_paths=True,
                 device_media_path="", ignore_folders=False, storage_path_separator=os.sep):
        self.device_media_path = device_media_path
        self.media_path = media_path
        self.playlist_path = playlist_path
        self.ignore_folders = ignore_folders
        self.use_related_paths = use_related_paths
        self.storage_path_separator = storage_path_separator

    @staticmethod
    def makedirs(fname):
        if not os.path.exists(os.path.dirname(fname)):
            try:
                os.makedirs(os.path.dirname(fname))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def save(self, path, content):
        path = path.replace(":", "_").replace("?", "_").replace("mtp_host", "mtp:host")
        self.assert_path_in_storage(path)
        self.makedirs(path)
        with codecs.open(path, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def content_equals(path, content):
        if os.path.exists(path):
            with codecs.open(path, "r", encoding="utf-8") as f:
                try:
                    cont = f.read()
                    return content == cont
                except IOError:
                    return False
        return False

    def copy(self, from_, to_):
        self.makedirs(to_)
        self.assert_path_in_storage(to_)
        if not os.path.exists(to_):
            try:
                if "mtp:" in to_:
                    subprocess.check_output(['gvfs-copy', from_, to_])
                else:
                    shutil.copy(from_, to_)

            except IOError as e:
                print(e)

    def assert_path_in_storage(self, path):
        assert self.media_path in path or self.playlist_path in path
