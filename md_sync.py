#!/usr/bin/python
# -*- coding: utf-8 -*-

from models import *


def syncMovie(l_movie):
    movies = Movie.select().where(Movie.movie_number == l_movie.number)
    if movies.count() == 0:
        print('        missing movie data: ' + l_movie.number)
        return

    movie = movies.get()
    if l_movie.video_status == 'FHD':
        movie.movie_status = 'fhd_done'
    elif l_movie.video_status == 'HD':
        movie.movie_status = 'hd_done'
    elif l_movie.video_status == 'SD':
        movie.movie_status = 'sd_done'

    movie.save()
    l_movie.video_sync = True
    l_movie.save()

def main():


    l_movies = L_JPN_Movie.select().where(L_JPN_Movie.video_sync == False)

    for l_movie in l_movies:
        print('begin to sync movie: ' + l_movie.number)
        syncMovie(l_movie)

if __name__ == '__main__':
    main()
