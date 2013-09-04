#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from os import listdir, stat
from stat import S_ISDIR

import commands

from models import *
import utils

dict = {}
dictUpdate = {}

dict_g = {}
dictUpdate_g = {}



def processVideo(fileName, collection):
    global dictUpdate

    file = fileName.split('/')[-1]
    fileData = file.split('_')

    actresses = fileData[1].split('&')
    for actress in actresses:
        ra = actress.replace('.', ' ').lower()
        if not dictUpdate.has_key(ra):
            dictUpdate[ra] = 0

        dictUpdate[ra] = dictUpdate[ra] + 1

    collection.path = fileName
    collection.video_extension = os.path.splitext(file)[-1]
    collection.video_size = utils.convertSize(os.path.getsize(fileName))

    rfileName = fileName.replace('&', '\&')
    command = 'mediainfo --Inform="Video;%Format%_%Width%X%Height%_%DisplayAspectRatio/String%_%Duration/String3%" ' + rfileName
    result = commands.getstatusoutput(command)

    if result[0] == 0:
        collection.video_resolution = result[1].split('_')[1]
        collection.video_aspect_ratio = result[1].split('_')[2]
        collection.video_duration = result[1].split('_')[3]
    else:
        print('execute mediainfo command error: ' + fileName)

    
    collection.video_status = 'UNKNOWN'

    # try:
    if not (collection.video_resolution is None):
        width = int(collection.video_resolution.split('X')[0])
        if width >= 1800:
            collection.video_status = 'FHD'
        elif width >= 1000:
            collection.video_status = 'HD'
        else:
            collection.video_status = 'SD'
    # except TypeError:
    #     print('')


    print('updating video info: ' + fileName)
    collection.save()

def processFile(fileName):
    global dict
    # print('********** ' + fileName + ' **********')
    file = fileName.split('/')[-1]
    dir = fileName.split('/')[-2]
    fileData = file.split('_')

    vendor = fileData[0]

    actresses = fileData[1].split('&')
    p_actresses = []
    for actress in actresses:
        newact = actress.replace('.', ' ').lower()
        if newact[-1] == ' ':
            realact = newact[:-1] + '.'
            p_actresses.append(realact)
        else:
            p_actresses.append(newact)


    name = ''
    index = 2
    count = len(fileData)
    while index < count - 1:
        name += fileData[index] + ' '
        index += 1
    name = name[:-1]

    if dict.has_key(name):
        print('local video file unique error: ')
        print('origin file: ' + dict[name])
        print('current file: ' + fileName)
        return
    
    dict[name] = fileName

    ext = fileData[-1].split('.')[0]

    actress_check = True
    exist_cols = L_XART_Collection.select().where((fn.Lower(L_XART_Collection.name) == name) & (L_XART_Collection.ctype == 'Movie'))
    if exist_cols.count() == 1:
        collection = exist_cols.get()
        c_actresses = collection.actress.split(':')
        pc_actresses = []
        for actress in c_actresses:
            pc_actresses.append(actress.lower())
        for actress in p_actresses:
            if actress not in pc_actresses:
                actress_check = False

        if actress_check == False:
            print('X-Art lib missing with actress: ' + dir + '/' + file)
        else: 
            processVideo(fileName, collection)
    elif exist_cols.count() == 0:
        print('X-Art lib missing: ' + dir + '/' + file)
    else:
        print('X-Art lib unique error: ' + dir + '/' + file)


def processDir(dirName):
    files = listdir(dirName)
    for file in files:
        fileName = os.path.join(dirName, file)
        st_values = stat(fileName)
        if S_ISDIR(st_values[0]):
            processDir(fileName)
        elif file[0] == '.':
            print('temp file error: ' + fileName)
        elif os.path.splitext(file)[-1] == '.avi' or os.path.splitext(file)[-1] == '.wmv' or \
            os.path.splitext(file)[-1] == '.mp4' or os.path.splitext(file)[-1] == '.mkv' or \
            os.path.splitext(file)[-1] == '.mov':
            processFile(fileName)
        else:
            print('unknown file type error: ' + fileName)


def processUpdate(actresses):
    global dictUpdate_g

    for actress in actresses:
        # ra = actress.replace('.', ' ').lower()
        if not dictUpdate_g.has_key(actress):
            dictUpdate_g[actress] = 0

        dictUpdate_g[actress] = dictUpdate_g[actress] + 1

def processDirInfo(subDir):
    global dict_g

    dirData = subDir.split('_')

    actresses = dirData[1].split('&')
    p_actresses = []
    for actress in actresses:
        p_actresses.append(actress.replace('.', ' ').lower())

    name = ''
    index = 2
    count = len(dirData)
    while index < count:
        name += dirData[index] + ' '
        index += 1
    name = name[:-1]

    if dict.has_key(name):
        print('local gallery file unique error: ')
        print('origin file: ' + dict[name])
        print('current file: ' + subDir)
        return
    
    dict[name] = subDir

    actress_check = True
    exist_cols = L_XART_Collection.select().where((fn.Lower(L_XART_Collection.name) == name) & (L_XART_Collection.ctype == 'Gallery'))
    if exist_cols.count() == 1:
        collection = exist_cols.get()
        c_actresses = collection.actress
        for actress in p_actresses:
            if not actress in c_actresses.lower():
                actress_check = False

        if actress_check == False:
            print('X-Art lib missing with actress: ' + subDir)
        else: 
            collection.video_status = 'OK'
            collection.save()
            processUpdate(p_actresses)
    elif exist_cols.count() == 0:
        print('X-Art lib missing: ' + subDir)
    else:
        print('X-Art lib unique error: ' + subDir)

def processDir_G(dirName):
    subDirs = listdir(dirName)
    for subDir in subDirs:
        subDirName = os.path.join(dirName, subDir)
        st_values = stat(subDirName)
        if S_ISDIR(st_values[0]):
            processDirInfo(subDir)
        else:
            print('bad dir structure: ' + subDirName)

def updateOwnCount():
    global dictUpdate
    for name, own_count in dictUpdate.items():
        print('updating video own_count info: ' + name)
        update_query = L_XART_Actress.update(movie_own_count=own_count).where(fn.Lower(L_XART_Actress.name) == name)
        update_query.execute()

def updateOwnCount_G():
    global dictUpdate_g
    for name, own_count in dictUpdate_g.items():
        print('updating gallery own_count info: ' + name)
        update_query = L_XART_Actress.update(gallery_own_count=own_count).where(fn.Lower(L_XART_Actress.name) == name)
        update_query.execute()

def main():
    top_dir = '/home/liyunhai/Share/mount/WEST/X-Art'
    # top_dir = '/home/liyunhai/Dev/X-Art'

    top_dir_g = '/home/liyunhai/Share/mount/WEST/X-Art-G'

    if len(sys.argv) == 1:
        processDir(top_dir)
        updateOwnCount()

        processDir_G(top_dir_g)
        updateOwnCount_G()
    elif len(sys.argv) == 2:
        if sys.argv[1] == 'movie':
            processDir(top_dir)
            updateOwnCount()
        elif sys.argv[1] == 'gallery':
            processDir_G(top_dir_g)
            updateOwnCount_G()

if __name__ == '__main__':
    main()
