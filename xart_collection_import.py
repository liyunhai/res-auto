#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib2
import socks
import socket
import httplib
from htmlparser import XartCollectionList
from models import *

gallery_count = 0
movie_count = 0

def recordError(module, message, detail):
    error = Error_History()
    error.error_module = module
    error.error_message = message
    error.error_detail = detail
    error.save()

def processActress(actress):

    try:
        global gallery_count
        global movie_count
        
        print('begin to process actress: ' + actress.name)
        
        single_gallery_count = 0
        single_movie_count = 0

        usock = urllib2.urlopen(actress.url, timeout=60)
        parser = XartCollectionList(actress)
        parser.feed(usock.read())
        usock.close()
        parser.close()

        index = 0
        collection_count = len(parser.collections)
        while index < collection_count:
            collection = parser.collections[collection_count - index - 1]
            exist_cols = L_XART_Collection.select().where((L_XART_Collection.name == collection.name) & (L_XART_Collection.actress == collection.actress) & (L_XART_Collection.ctype == collection.ctype))
            if exist_cols.count() == 0:
                try:
                    collection.save()
                except UnicodeDecodeError, e:
                    print('UnicodeDecodeError: ' + collection.actress + ' ' + collection.name + ' ' + collection.ctype + ' [' + str(exist_cols.count()) +']')
                    collection.desc = 'UnicodeDecodeError'
                    collection.save()
                
                if collection.ctype == 'Gallery':
                    gallery_count += 1
                elif collection.ctype == 'Movie':
                    movie_count += 1
            else:
                print('        unique warning: ' + collection.actress + ' ' + collection.name + ' ' + collection.ctype + ' [' + str(exist_cols.count()) +']')

            if collection.ctype == 'Gallery':
                single_gallery_count += 1
            elif collection.ctype == 'Movie':
                single_movie_count += 1
            index += 1

        actress.gallery_count = single_gallery_count
        actress.movie_count = single_movie_count
        actress.save()

        # gallery_count += single_gallery_count
        # movie_count += single_movie_count

        print('end process actress: ' + actress.name + '[G:' + str(single_gallery_count) + ' M:' + str(single_movie_count) + ']')
    
    except urllib2.HTTPError, e:
        recordError('XART_COLLECTION_IMPORT', str(e), actress.name)
        print e
    except urllib2.URLError, e:
        recordError('XART_COLLECTION_IMPORT', str(e), actress.name)
        print e
    except socket.timeout, e:
        recordError('XART_COLLECTION_IMPORT', str(e), actress.name)
        print e
    except socket.error, e:
        recordError('XART_COLLECTION_IMPORT', str(e), actress.name)
        print e
    except httplib.BadStatusLine, e:
        recordError('XART_COLLECTION_IMPORT', str(e), actress.name)
        print e
    # finally:
    #     if not usock is None:
    #         usock.close()
    #     if not parser is None:
    #         parser.close()

def main():
    global gallery_count
    global movie_count

    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 7070)
    socket.socket = socks.socksocket
    
    actresses = []

    if len(sys.argv) == 1:
        actresses = L_XART_Actress.select()
    elif len(sys.argv) == 2:
        actresses = L_XART_Actress.select().where(L_XART_Actress.name == sys.argv[1])

    for actress in actresses:
        processActress(actress)

    print('total process Galley: ' + str(gallery_count) + ' & Movie: ' + str(movie_count))

if __name__ == '__main__':
    main()