#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib2
import socket
import httplib
from sgmllib import SGMLParser, SGMLParseError
from htmlparser import XartMagnetList
from models import *

def recordError(module, message, detail):
    error = Error_History()
    error.error_module = module
    error.error_message = message
    error.error_detail = detail
    error.save()

def processCollection(collection):

    try:
        url_pre = 'http://kickass.to/usearch/x-art%20'
        search_tag = collection.name.replace(' ', '%20')
        url = url_pre + search_tag + '/'
        print(url)
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36", \
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
        request = urllib2.Request(url, headers=headers)
        usock = urllib2.urlopen(request, timeout=120)
        parser = XartMagnetList(collection)
        parser.feed(usock.read())
        usock.close()
        parser.close()

        # index = 0
        # magnet_count = len(parser.magnets)
        # while index < magnet_count:
        #     magnet = parser.magnets[magnet_count - index - 1]
        #     magnet.save()
        #     index += 1

        # if magnet_count != 0:
        #     movie.movie_magnet_count += magnet_count
        #     movie.save()
    except urllib2.HTTPError, e:
        recordError('XART_MAGNET', str(e), collection.name)
        collection.video_status = '404'
        collection.save()
        print e
    except urllib2.URLError, e:
        recordError('XART_MAGNET', str(e), collection.name)
        print e
    except socket.timeout, e:
        recordError('XART_MAGNET', str(e), collection.name)
        print e
    except socket.error, e:
        recordError('XART_MAGNET', str(e), collection.name)
        print e
    except httplib.BadStatusLine, e:
        recordError('XART_MAGNET', str(e), collection.name)
        print e
    except SGMLParseError, e:
        recordError('XART_MAGNET', str(e), collection.name)
        collection.video_status = 'SGML'
        collection.save()
        print e

def main():
    collections = L_XART_Collection.select().where((L_XART_Collection.ctype == 'Gallery') & (L_XART_Collection.video_status >> None))

    for collection in collections:
        print('begin to process collection: ' + collection.name)
        processCollection(collection)

if __name__ == '__main__':
    main()