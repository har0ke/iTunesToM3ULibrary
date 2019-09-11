# -*- coding: utf-8 -*-
import argparse
import os

from configuration import Configuration
from itunes_library import ITunesLibrary
from m3u_storage import M3UStorage
from synchronisation import LibrarySynchronisation

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("conf_file", help="Configuration file <settings>.json")
    options = parser.parse_args()

    configuration = Configuration(options.conf_file)

    library = ITunesLibrary(configuration.itunes_media_path, configuration.itunes_library,
                            configuration.itunes_media_db_path)
    storage = M3UStorage(configuration.storage_copy_media_path, configuration.storage_copy_playlist_path,
                         configuration.relative_paths, configuration.storage_m3u_media_path, configuration.ignore_folders,
                         configuration.storage_path_separator)
    connector = LibrarySynchronisation(library, storage)

    for song in library.songs.values():
        if song.location and not song.location.startswith(library.media_path):
            raise Exception("library internal path does not seem to be right: %s" % library.songs[
                library.songs.keys()[0]].location)

    all_playlists = set(library.play_lists)

    g = lambda x: {library.get_play_lists_by_full_name(x)}
    s = lambda x: set(library.find_play_lists_by_full_name(x))

    include = set([])
    for i in configuration.include:
        if i.startswith("get_"):
            include.update(g(i[4:]))
        elif i.startswith("search_"):
            include.update(s(i[7:]))
        elif i == "all":
            include.update(all_playlists)
        else:
            raise Exception("Missconfiguration: objects in EXCLUDE must start with 'get' or 'search'")

    exclude = set([])
    for i in configuration.exclude:
        if i.startswith("get"):
            exclude.update(g(i[4:]))
        elif i.startswith("search"):
            exclude.update(s(i[7:]))
        else:
            raise Exception("Missconfiguration: objects in EXCLUDE must start with 'get' or 'search'")

    connector.add(include - exclude)
    connector.sync(True, configuration.cleanup_media_copy_storage)
