#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import socket
from datetime import datetime
from sgmllib import SGMLParser
from models import Actress, Movie, Magnet

class FanHaoList(SGMLParser):

    def __init__(self, last_time):
        SGMLParser.__init__(self)
        self.last_time = last_time
        self.break_tag = False
        self.start_tag = False
        self.tbody_tag = False
        self.is_a = False
        self.is_td = False
        self.td_index = -1
        self.movies = []

    def reset(self):
        SGMLParser.reset(self)
        self.break_tag = False
        self.start_tag = False
        self.tbody_tag = False
        self.is_a = False
        self.is_td = False
        self.td_index = -1
        self.movies = []

    def start_table(self, attrs):
        if self.break_tag == True:
            return
        
        for attr in attrs:
            if attr[0] == 'class' and attr[1] == 'fanhao_list_table':
                self.start_tag = True

    def start_tbody(self, attrs):
        if self.break_tag == True:
            return
        
        if self.start_tag == True:
            self.tbody_tag = True

    def end_tbody(self):
        if self.break_tag == True:
            return
        
        self.tbody_tag = False

    def start_tr(self, attrs):
        if self.break_tag == True:
            return

        if self.start_tag == True and self.tbody_tag == True:
            movie = Movie()
            movie.movie_status = 'new'
            movie.movie_magnet_count = 0
            self.movies.append(movie)

    def end_tr(self):
        if self.break_tag == True:
            return

        self.td_index = -1

    def start_td(self, attrs):
        if self.break_tag == True:
            return

        if self.start_tag != True or self.tbody_tag != True:
            return

        self.td_index += 1
        self.is_td = True

    def end_td(self):
        if self.break_tag == True:
            return

        self.is_td = False

    def start_a(self, attrs):
        if self.break_tag == True:
            return

        if self.start_tag != True or self.tbody_tag != True:
            return

        movie = self.movies[-1]
        if self.td_index == 0:
            href = [v for k, v in attrs if k=='href']
            if href:
                try:
                    fanhao_usock = urllib2.urlopen(href[0], timeout=60)
                    fanhao_parser = FanHao()
                    fanhao_parser.feed(fanhao_usock.read())
                    fanhao_usock.close()
                    fanhao_parser.close()

                    movie.movie_multi_a = len(fanhao_parser.actresses)
                    movie.movie_actress = ' '.join(fanhao_parser.actresses)
                    movie.movie_desc = fanhao_parser.desc

                    if movie.movie_multi_a > 4:
                        movie.movie_status = 'multi'
                except urllib2.HTTPError, e:
                    if e.code == 404:
                        movie.movie_multi_a = 0
                        movie.movie_actress = ' '
                        movie.movie_desc = 'unknown because of 404'
                        movie.movie_status = 'unknown'
                    else:
                        raise e
                except urllib2.URLError, e:
                    raise e
                except socket.timeout, e:
                    raise e
                # finally:
                #     if not fanhao_usock is None:
                #         fanhao_usock.close()
                #     if not fanhao_parser is None:
                #         fanhao_parser.close()

        self.is_a = True

    def end_a(self):
        if self.break_tag == True:
            return

        self.is_a = False

    def handle_data(self, text):
        if self.break_tag == True:
            return

        if self.start_tag != True or self.tbody_tag != True:
            return

        if self.is_a != True and self.is_td != True:
            return

        movie = self.movies[-1]
        if self.td_index == 0:
            movie.movie_number = text
            print('    processing movie: ' + movie.movie_number)
            if movie.movie_multi_a > 1 and Movie.select().where(Movie.movie_number == movie.movie_number).count() >= 1:
                print('        unique check failed(multi): ' + movie.movie_number)
                movie.movie_status = 'exist'
        elif self.td_index == 1:
            movie.movie_name = text
        elif self.td_index == 2:
            movie.movie_duration = text
        elif self.td_index == 3:
            movie.movie_release_date = datetime.strptime(text, "%Y-%m-%d").date()
            if movie.movie_release_date == self.last_time:
                if Movie.select().where(Movie.movie_number == movie.movie_number).count() >= 1:
                    print('        unique check failed(last time): ' + movie.movie_number)
                    del self.movies[-1]
                    self.break_tag = True
                    if len(self.movies) == 0:
                        print('******************** no movie update ********************')
            elif movie.movie_release_date < self.last_time:
                print('        unique check failed(last time): ' + movie.movie_number)
                del self.movies[-1]
                self.break_tag = True
                if len(self.movies) == 0:
                    print('******************** no movie update ********************')
        elif self.td_index == 4:
            movie.movie_press = text

class FanHao(SGMLParser):
    td_tag = ''
    is_a = False
    desc = ''
    actresses = []
    
    def reset(self):
        SGMLParser.reset(self)
        self.td_tag = ''
        self.is_a = False
        self.desc = ''
        self.actresses = []

    def start_td(self, attrs):
        for attr in attrs:
            if attr[0] == 'class' and attr[1] == 'peoples':
                self.td_tag = 'peoples'
            if attr[0] == 'class' and attr[1] == 'desc':
                self.td_tag = 'desc'

    def end_td(self):

        self.td_tag = ''

    def start_a(self, attrs):
        if self.td_tag != 'peoples':
            return

        self.is_a = True

    def end_a(self):
        self.is_a = False

    def handle_data(self, text):
        if self.td_tag == 'desc':
            self.desc = text
        elif self.td_tag == 'peoples' and self.is_a == True:
            self.actresses.append(text)

class MagnetList(SGMLParser):

    
    def __init__(self, movie):
        SGMLParser.__init__(self)
        self.movie = movie
        self.break_tag = False
        self.start_tag = False
        self.td_tag = ''
        self.is_td = False
        self.tr_index = 0
        self.a_index = 0

        self.magnets = []

    def reset(self):
        SGMLParser.reset(self)
        self.break_tag = False
        self.start_tag = False
        self.td_tag = ''
        self.is_td = False
        self.tr_index = 0
        self.a_index = 0

        self.magnets = []

    def start_table(self, attrs):
        if self.break_tag == True:
            return
        
        for attr in attrs:
            if attr[0] == 'id' and attr[1] == 'archiveResult':
                self.start_tag = True

    def end_table(self):
        if self.break_tag == True:
            return

        self.start_tag = False
        

    def checkUnique(self, pre_magnet):
        count = Magnet.select().where((Magnet.magnet_desc == pre_magnet.magnet_desc) & \
            (Magnet.magnet_upload_date == pre_magnet.magnet_upload_date)).count()
        if  count >= 1:
            print('        unique check failed: ' + pre_magnet.magnet_desc)
            return False

        return True

    def checkAccuracy(self, pre_magnet):

        keys = self.movie.movie_number.split('-')
        p1 = self.movie.movie_number.lower()
        p2 = (keys[0] + keys[1]).lower()
        p3 = (keys[0] + '00' + keys[1]).lower()

        udesc = unicode(pre_magnet.magnet_desc.lower(), "utf-8")

        if udesc.find(p1) != -1:
            return True

        if udesc.find(p2) != -1:
            return True

        if udesc.find(p3) != -1:
            return True

        print('        accuracy check failed: ' + pre_magnet.magnet_desc)
        return False

    def start_tr(self, attrs):
        if self.break_tag == True:
            return

        if self.start_tag == True:
            if self.tr_index != 0:
                magnet = Magnet()
                magnet.movie = self.movie
                self.magnets.append(magnet)
            self.tr_index += 1

    def end_tr(self):
        if self.break_tag == True:
            return

        self.td_tag = ''

        if len(self.magnets) >= 1:
            pre_magnet = self.magnets[-1]
            if self.checkUnique(pre_magnet) == False:
                del self.magnets[-1]
                self.break_tag = True
                if len(self.magnets) == 0:
                    print('******************** no magnet update ********************')
                return

            if self.checkAccuracy(pre_magnet) == False:
                del self.magnets[-1]

    def start_td(self, attrs):
        if self.break_tag == True:
            return

        if self.start_tag != True:
            return

        for attr in attrs:
            if attr[0] == 'class' and attr[1] == 'name':
                self.td_tag = 'desc'
            elif attr[0] == 'class' and attr[1] == 'date':
                self.td_tag = 'upload date'
            elif attr[0] == 'class' and attr[1] == 'action':
                self.td_tag = 'action'
            else:
                self.td_tag = ''


        self.is_td = True

    def end_td(self):
        if self.break_tag == True:
            return

        self.is_td = False
        self.a_index = 0

    def start_a(self, attrs):
        if self.break_tag == True:
            return

        if self.start_tag != True:
            return

        magnet = self.magnets[-1]
        if self.td_tag == 'action':
            href = [v for k, v in attrs if k=='href']
            if href and self.a_index == 0:
                try:
                    magnet.magnet_web_url = 'http://www.torrentkitty.com' + href[0]

                    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36", \
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
                    request = urllib2.Request(magnet.magnet_web_url, headers=headers)
                    print('    processing magnet: ' + magnet.magnet_desc)
                    magnet_usock = urllib2.urlopen(request, timeout=120)
                    magnet_parser = MagnetInfo()
                    magnet_parser.feed(magnet_usock.read())
                    magnet_usock.close()
                    magnet_parser.close()

                    magnet.magnet_size = magnet_parser.size
                    magnet.magnet_size_number = magnet_parser.size_number
                    magnet.magnet_files_count = magnet_parser.files_count

                except urllib2.HTTPError, e:
                    if e.code == 404:
                        magnet.magnet_size = '0M'
                        magnet.magnet_size_number = 0
                        magnet.magnet_files_count = 0
                    else:
                        raise e
                except urllib2.URLError, e:
                    raise e
                except socket.timeout, e:
                    raise e

            elif href and self.a_index == 1:
                magnet.magnet_link = href[0]

            self.a_index += 1

    def handle_data(self, text):
        if self.break_tag == True:
            return

        if self.start_tag != True:
            return

        if self.is_td != True:
            return

        magnet = self.magnets[-1]
        if self.td_tag == 'desc':
            magnet.magnet_desc = text
        elif self.td_tag == 'upload date':
            magnet.magnet_upload_date = datetime.strptime(text, "%b %d, %Y").date()

class MagnetInfo(SGMLParser):
    td_tag = ''
    is_th = False
    is_td = False
    size = ''
    size_number = 0
    files_count = 0
    
    def convertSize(self, size):
        size_n = 0

        sizes = size.split(' ')

        if len(sizes) == 2:
            if sizes[1] == 'MB':
                size_n = float(sizes[0])
            elif sizes[1] == 'GB':
                size_n = float(sizes[0]) * 1024
            elif sizes[1] == 'TB':
                size_n = float(sizes[0]) * 1024 * 1024
            elif sizes[1] == 'KB':
                size_n = float(sizes[0]) / 1024

        return size_n

    def reset(self):
        SGMLParser.reset(self)
        self.td_tag = ''
        self.is_th = False
        self.is_td = False
        self.size = ''
        self.size_number = 0
        self.files_count = 0

    def start_th(self, attrs):
        self.is_th = True

    def end_th(self):
        self.is_th = False

    def start_td(self, attrs):
        self.is_td = True

    def end_td(self):
        self.is_td = False
        self.td_tag = ''

    def handle_data(self, text):
        if self.is_th == True:
            if text == 'Number of Files:':
                self.td_tag = 'files_count'
            elif text == 'Content Size:':
                self.td_tag = 'size'
        elif self.is_td == True:
            if self.td_tag == 'files_count':
                self.files_count = int(text)
            elif self.td_tag == 'size':
                self.size = text
                self.size_number = self.convertSize(self.size)
