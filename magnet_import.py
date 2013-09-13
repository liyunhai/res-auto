#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib2
import socket
import httplib
from htmlparser import MagnetList
from datetime import date
from datetime import datetime
from datetime import timedelta
from models import *

def recordError(module, message, detail):
    error = Error_History()
    error.error_module = module
    error.error_message = message
    error.error_detail = detail
    error.save()

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

        if(movie.movie_status == 'new') or (movie.movie_status == 'multi') or (movie.movie_status == 'import_dead'):
            if magnet_count != 0:
                movie.movie_status = 'import_done'
                movie.movie_magnet_count = magnet_count
            else:
                today = date.today()
                days = (today - movie.movie_release_date).days
                if days > 90:
                    movie.movie_status = 'import_dead'
            movie.save()
        else:
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
    except socket.error, e:
        recordError('MAGNET_IMPORT', str(e), movie.movie_number + ' ' + movie.movie_name)
        print e
    except httplib.BadStatusLine, e:
        recordError('MAGNET_IMPORT', str(e), movie.movie_number + ' ' + movie.movie_name)
        print e

def main():
    movies = []

    if len(sys.argv) == 1:
        movies = Movie.select().where((Movie.movie_status != 'fhd_done') & (Movie.movie_status != 'multi'))
    elif len(sys.argv) == 2:
        if sys.argv[1] == 'new':
            movies = Movie.select().where(Movie.movie_status == 'new')
        elif sys.argv[1] == 'multi':
            movies = Movie.select().where(Movie.movie_status == 'multi')
        elif sys.argv[1] == 'fordead':
            day = date.today() + timedelta(-90)
            movies = Movie.select().where((Movie.movie_status == 'import_dead') & (Movie.movie_release_date > day))
        elif sys.argv[1] == 'forupdate':
            day = date.today() + timedelta(-90)
            movies = Movie.select().where((Movie.movie_status == 'import_done') & (Movie.movie_release_date > day))
        elif sys.argv[1] == 'forhd':
            movies = Movie.select().where((Movie.movie_status == 'hd_done') | (Movie.movie_status == 'sd_done')) 
        else:
            actress = u'%' + sys.argv[1].decode('utf-8') + u'%'
            movies = Movie.select().where((Movie.movie_status != 'fhd_done') & (Movie.movie_status != 'multi') & (Movie.movie_actress % actress))
    for movie in movies:
        print('begin to process movie: ' + movie.movie_number + ' ' + movie.movie_name)
        processMovie(movie)

if __name__ == '__main__':
    main()
