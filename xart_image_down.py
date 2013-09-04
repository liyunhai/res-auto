#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
# from os import listdir, stat
# from stat import S_ISDIR

import urllib2
import socket
import httplib
from models import *


base_dir = '/home/liyunhai/Dev/X-ART'

def recordError(module, message, detail):
    error = Error_History()
    error.error_module = module
    error.error_message = message
    error.error_detail = detail
    error.save()


def create_dir(dir):
    if os.path.exists(dir):
        return

    print('creating dir: ' + dir)
    os.mkdir(dir)

def down_image(url, dir):
    fileName = url.split('/')[-1].replace('%20', '_')
    fullName = os.path.join(dir, fileName)

    if os.path.isfile(fullName):
        return

    print('downloading file: ' + url)
    
    try:

        usock = urllib2.urlopen(url, timeout=60)
        data = usock.read()
        usock.close()

        image = file(fullName, 'wb')
        image.write(data)
        image.close()
    
    except urllib2.HTTPError, e:
        recordError('XART_IMAGE_DOWN', str(e), url)
        print e
    except urllib2.URLError, e:
        recordError('XART_IMAGE_DOWN', str(e), url)
        print e
    except socket.timeout, e:
        recordError('XART_IMAGE_DOWN', str(e), url)
        print e
    except socket.error, e:
        recordError('XART_IMAGE_DOWN', str(e), url)
        print e
    except httplib.BadStatusLine, e:
        recordError('XART_IMAGE_DOWN', str(e), url)
        print e


def actress_down():
    global base_dir

    actresses = L_XART_Actress.select()
    for actress in actresses:
        name = actress.name.replace('.', '').replace(' ', '_')
        dir = os.path.join(base_dir, name)
        
        create_dir(dir)
        down_image(actress.image_large, dir)


def collection_down():
    collection = L_XART_Collection.select()
    for collection in collections:
        name = collection.name.replace('', '_')
        dir = os.path.join(base_dir, name)
        
        create_dir(dir)
        # down_image(actress.image_small, dir)
        down_image(actress.image_large, dir)
    pass


def main():

    actress_down()

    collection_down()

    # print('total process Galley: ' + str(gallery_count) + ' & Movie: ' + str(movie_count))

if __name__ == '__main__':
    main()