#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib2
import socket
import httplib
from htmlparser import FanHaoList
from pymediainfo import MediaInfo
# from utils import recordError
from models import *

import os
from os import listdir, stat
from stat import S_ISDIR

# def recordError(module, message, detail):
#     error = Error_History()
#     error.error_module = module
#     error.error_message = message
#     error.error_detail = detail
#     error.save()

# def processActress(actress):

#     try:
#         last_time = actress.actress_last_time

#         usock = urllib2.urlopen(actress.actress_url, timeout=60)
#         parser = FanHaoList(last_time)
#         parser.feed(usock.read())
#         usock.close()
#         parser.close()

#         index = 0
#         movie_count = len(parser.movies)
#         while index < movie_count:
#             movie = parser.movies[movie_count - index - 1]
#             if movie.movie_status != 'exist':
#                 movie.save()
#                 last_time = movie.movie_release_date
#             index += 1

#         if last_time != actress.actress_last_time:
#             actress.actress_last_time = last_time
#             actress.save()
#     except urllib2.HTTPError, e:
#         recordError('MD_IMPORT', str(e), actress.actress_name)
#         print e
#     except urllib2.URLError, e:
#         recordError('MD_IMPORT', str(e), actress.actress_name)
#         print e
#     except socket.timeout, e:
#         recordError('MD_IMPORT', str(e), actress.actress_name)
#         print e
#     except socket.error, e:
#         recordError('MD_IMPORT', str(e), actress.actress_name)
#         print e
#     except httplib.BadStatusLine, e:
#         recordError('MD_IMPORT', str(e), actress.actress_name)
#         print e
    # finally:
    #     if not usock is None:
    #         usock.close()
    #     if not parser is None:
    #         parser.close()

def main():
    top_dir = '/home/liyunhai/Share/mnt/JPN'
    actresses_dir = listdir(top_dir)
    for actress_dir in actresses_dir:
        full_actress_dir = os.path.join(top_dir, actress_dir)
        st_a_values = stat(full_actress_dir)
        if S_ISDIR(st_a_values[0]):
            print('begin import actress: ' + actress_dir)
            movies_dir = listdir(full_actress_dir)
            for movie_dir in movies_dir:
                full_movie_dir = os.path.join(full_actress_dir, movie_dir)
                st_m_values = stat(full_movie_dir)
                if S_ISDIR(st_m_values[0]):
                    print('        begin import movie: ' + movie_dir)
                else:
                    print('        structure error: ' + full_movie_dir)
                

        else:
            print('structure error: ' + full_actress_dir)

    # actresses = []

    # if len(sys.argv) == 1:
    #     actresses = Actress.select()
    # elif len(sys.argv) == 2:
    #     actresses = Actress.select().where(Actress.actress_name == sys.argv[1].decode('utf-8'))

    # for actress in actresses:
    #     print('begin to process actress: ' + actress.actress_name)
    #     processActress(actress)
    # media_info = MediaInfo.parse('/home/liyunhai/Dev/testfile/xart.13.07.25.jessica.make.me.feel.beautiful.mp4')
    # for track in media_info.tracks:
    #     if track.track_type == 'Video':
    #         print track.width, track.height

    # media_info = MediaInfo.parse('/home/liyunhai/Dev/testfile/xart.13.07.25.jessica.make.me.feel.beautiful.mp4')
    # for track in media_info.tracks:
    #     if track.bit_rate is not None:
    #         print "%s: %s" % (track.track_type, track.bit_rate)
    #     else:
    #         print "%s tracks do not have bit rate associated with them." % track.track_type

if __name__ == '__main__':
    main()
