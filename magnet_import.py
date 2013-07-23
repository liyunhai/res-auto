#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import socket
import httplib
from htmlparser import MagnetList
from utils import recordError
from models import *

def processMovie(movie):

    try:
        url_pre = 'http://www.torrentkitty.com/search/'
        search_tag = movie.movie_number.replace('-', '%20')
        url = url_pre + search_tag + '/'
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36", \
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
        request = urllib2.Request(url, headers=headers)
        usock = urllib2.urlopen(request, timeout=120)
        parser = MagnetList(movie)
        parser.feed(usock.read())
        usock.close()
        parser.close()

        index = 0
        magnet_count = len(parser.magnets)
        while index < magnet_count:
            magnet = parser.magnets[magnet_count - index - 1]
            magnet.save()
            index += 1

        if magnet_count != 0:
            movie.movie_magnet_count += magnet_count
            movie.save()
    except urllib2.HTTPError, e:
        recordError('MAGNET_IMPORT', str(e), movie.movie_number + ' ' + movie.movie_name)
        print e
    except urllib2.URLError, e:
        recordError('MAGNET_IMPORT', str(e), movie.movie_number + ' ' + movie.movie_name)
        print e
    except socket.timeout, e:
        recordError('MAGNET_IMPORT', str(e), movie.movie_number + ' ' + movie.movie_name)
        print e
    except httplib.BadStatusLine, e:
        recordError('MAGNET_IMPORT', str(e), movie.movie_number + ' ' + movie.movie_name)
        print e

def main():
    for movie in Movie.select().where((Movie.movie_magnet_count == 0) & (Movie.movie_status == 'new')):
        print('begin to process movie: ' + movie.movie_number + ' ' + movie.movie_name)
        processMovie(movie)

if __name__ == '__main__':
    main()
