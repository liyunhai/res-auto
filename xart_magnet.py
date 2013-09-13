#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib2
import socket
import httplib
import gzip
import StringIO

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
        # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36", \
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
        # request = urllib2.Request(url, headers=headers)
        request = urllib2.Request(url)
        usock = urllib2.urlopen(request, timeout=120)

        rawdata = usock.read()
        data = StringIO.StringIO(rawdata)
        gz = gzip.GzipFile(fileobj=data)
        rawdata = gz.read()
        gz.close()

        parser = XartMagnetList(collection)
        parser.feed(rawdata)
        usock.close()
        parser.close()

        index = 0
        pic_count = 0
        magnet_count = len(parser.magnets)
        print(magnet_count)
        while index < magnet_count:
            magnet = parser.magnets[magnet_count - index - 1]
            if magnet.type == 'torType pictureType':
                pic_count += 1
                magnet.save()
            index += 1

        if pic_count != 0:
            collection.video_status = 'DOWNLOAD'
        else:
            collection.video_status = 'NOPIC'
        collection.save()
    
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
    collections = L_XART_Collection.select().where((L_XART_Collection.ctype == 'Gallery') & (L_XART_Collection.video_status == '404'))

    for collection in collections:
        print('begin to process collection: ' + collection.name)
        processCollection(collection)

if __name__ == '__main__':
    main()