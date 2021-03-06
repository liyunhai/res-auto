#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib2
import socket
import httplib
from htmlparser import FanHaoList
# from utils import recordError
from models import *

def recordError(module, message, detail):
    error = Error_History()
    error.error_module = module
    error.error_message = message
    error.error_detail = detail
    error.save()

def processActress(actress):

    try:
        last_time = actress.actress_last_time

        usock = urllib2.urlopen(actress.actress_url, timeout=60)
        parser = FanHaoList(last_time)
        parser.feed(usock.read())
        usock.close()
        parser.close()

        index = 0
        movie_count = len(parser.movies)
        while index < movie_count:
            movie = parser.movies[movie_count - index - 1]
            if movie.movie_status != 'exist':
                movie.save()
                last_time = movie.movie_release_date
            index += 1

        if last_time != actress.actress_last_time:
            actress.actress_last_time = last_time
            actress.save()
    except urllib2.HTTPError, e:
        recordError('MD_IMPORT', str(e), actress.actress_name)
        print e
    except urllib2.URLError, e:
        recordError('MD_IMPORT', str(e), actress.actress_name)
        print e
    except socket.timeout, e:
        recordError('MD_IMPORT', str(e), actress.actress_name)
        print e
    except socket.error, e:
        recordError('MD_IMPORT', str(e), actress.actress_name)
        print e
    except httplib.BadStatusLine, e:
        recordError('MD_IMPORT', str(e), actress.actress_name)
        print e
    # finally:
    #     if not usock is None:
    #         usock.close()
    #     if not parser is None:
    #         parser.close()

def main():
    actresses = []

    if len(sys.argv) == 1:
        actresses = Actress.select()
    elif len(sys.argv) == 2:
        actresses = Actress.select().where(Actress.actress_name == sys.argv[1].decode('utf-8'))

    for actress in actresses:
        print('begin to process actress: ' + actress.actress_name)
        processActress(actress)
        # print('end process actress:' + actress.actress_name)

if __name__ == '__main__':
    main()
