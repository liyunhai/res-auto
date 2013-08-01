#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from os import listdir, stat
from stat import S_ISDIR

import commands

from models import *
import utils

def processVideo(movie_dir, l_movie):
    l_movie.video_number = 0
    video_size = 0
    l_movie.video_resolution = ''
    l_movie.video_aspect_ratio = ''

    video_files = listdir(movie_dir)
    for video_file in video_files:
        full_video_file = os.path.join(movie_dir, video_file)
        st_values = stat(full_video_file)
        if S_ISDIR(st_values[0]):
            print('structure error: ' + full_video_file)
        elif os.path.splitext(video_file)[-1] == '.avi' or os.path.splitext(video_file)[-1] == '.wmv' or \
            os.path.splitext(video_file)[-1] == '.mp4' or os.path.splitext(video_file)[-1] == '.mkv' or \
            os.path.splitext(video_file)[-1] == '.mov':
            l_movie.video_number += 1
            l_movie.video_extension = os.path.splitext(video_file)[-1]
            video_size = video_size + os.path.getsize(full_video_file)

            command = 'mediainfo --Inform="Video;%Format%_%Width%X%Height%_%DisplayAspectRatio/String%" ' + full_video_file
            result = commands.getstatusoutput(command)

            if result[0] == 0:
                l_movie.video_codec = result[1].split('_')[0]
                l_movie.video_resolution = l_movie.video_resolution + result[1].split('_')[1] + ';'
                l_movie.video_aspect_ratio = l_movie.video_aspect_ratio + result[1].split('_')[2] + ';'
            else:
                print('execute mediainfo command error: ' + full_video_file)
        elif os.path.splitext(video_file)[-1] == '.jpg' or os.path.splitext(video_file)[-1] == '.png':
            pass
        else:
            print('unknown file type error: ' + full_movie_dir)
    
    l_movie.video_status = 'UNKNOWN'

    if l_movie.video_resolution != '':
        l_movie.video_resolution = l_movie.video_resolution[0:-1]
        width = int(l_movie.video_resolution.split(';')[0].split('X')[0])
        if width >= 1920:
            l_movie.video_status = 'FHD'
        elif width >= 1280:
            l_movie.video_status = 'HD'
        else:
            l_movie.video_status = 'SD'

    if l_movie.video_aspect_ratio != '':
        l_movie.video_aspect_ratio = l_movie.video_aspect_ratio[0:-1]
    
    l_movie.video_size = utils.convertSize(video_size)

def processMovie(movie_dir, index, movie_numbers):
    movie_dir_last = movie_dir.split('/')[-1]
    movie_number = movie_dir_last.split('_')[0]
    if not movie_number in movie_numbers:
        print('        begin import movie: ' + movie_dir_last)
        
        check_movies = L_JPN_Movie.select().where(L_JPN_Movie.number == movie_number)
        if check_movies.count() != 0:
            print('unique error: ' + movie_dir_last)
            return

        l_movie = L_JPN_Movie()
        l_movie.number = movie_number
        l_movie.video_path = movie_dir.split('/')[-2] + '/' + movie_dir.split('/')[-1]

        processVideo(movie_dir, l_movie)

        info = movie_dir_last + '\n'

        movies = Movie.select().where(Movie.movie_number == movie_number)
        if movies.count() != 0:
            movie = movies.get()
            l_movie.name = movie.movie_name
            l_movie.duration = movie.movie_duration
            l_movie.actress = movie.movie_actress
            l_movie.release_date = movie.movie_release_date
            l_movie.press = movie.movie_press
            l_movie.desc = movie.movie_desc
            info = l_movie.number + '_' + l_movie.name.encode('utf-8') + '\n'

        l_movie.save()

        index.write(info)
            

def processActress(actress_dir):
    print('begin import actress: ' + actress_dir.split('/')[-1])

    movie_numbers = []
    
    index = file(os.path.join(actress_dir, 'index.txt'), 'a+')
    while True:
        line = index.readline()
        if len(line) == 0: # Zero length indicates EOF
            break
        movie_numbers.append(line.split('_')[0])
    
    movies_dir = listdir(actress_dir)
    for movie_dir in movies_dir:
        full_movie_dir = os.path.join(actress_dir, movie_dir)
        st_values = stat(full_movie_dir)
        if S_ISDIR(st_values[0]):
            processMovie(full_movie_dir, index, movie_numbers)
        elif movie_dir == 'index.txt':
            pass
        else:
            print('structure error: ' + full_movie_dir)
    index.close()

def main():
    top_dir = '/home/liyunhai/Share/mnt/JPN'
    top_dir = '/home/liyunhai/Dev/testfile'
    actresses_dir = listdir(top_dir)
    for actress_dir in actresses_dir:
        full_actress_dir = os.path.join(top_dir, actress_dir)
        st_values = stat(full_actress_dir)
        if S_ISDIR(st_values[0]):
            processActress(full_actress_dir)
        else:
            print('structure error: ' + full_actress_dir)

if __name__ == '__main__':
    main()
