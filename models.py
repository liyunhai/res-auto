from hashlib import md5, sha1
from datetime import datetime
import string
import cPickle

from flask_peewee.auth import BaseUser
from peewee import *
from flask import Markup

from app import db

import utils

command_db = MySQLDatabase('res_auto', host='127.0.0.1', port=3306, user='res_auto', passwd='no1Knows')


class User(db.Model, BaseUser):
    username = CharField()
    password = CharField()
    email = CharField()
    join_date = DateTimeField(default=datetime.now)
    active = BooleanField(default=True)
    admin = BooleanField(default=False)

    def __unicode__(self):
        return self.username

    # def following(self):
    #     return User.select().join(
    #         Relationship, on=Relationship.to_user
    #     ).where(Relationship.from_user==self).order_by(User.username)

    # def followers(self):
    #     return User.select().join(
    #         Relationship, on=Relationship.from_user
    #     ).where(Relationship.to_user==self).order_by(User.username)

    # def is_following(self, user):
    #     return Relationship.select().where(
    #         Relationship.from_user==self,
    #         Relationship.to_user==user
    #     ).exists()

    # def gravatar_url(self, size=80):
    #     return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
    #         (md5(self.email.strip().lower().encode('utf-8')).hexdigest(), size)

class Rss(db.Model):
    rss_name = CharField(verbose_name='Name')
    rss_url = CharField(verbose_name='URL')
    rss_desc = TextField(verbose_name='Description')
    rss_last_time = DateTimeField(verbose_name='Last Time')
    
    def __unicode__(self):
        # return 'rss_name:%s rss_url:%s rss_desc:%s rss_last_time:%s' % \
        #        (self.rss_name, self.rss_url, self.rss_desc, self.rss_last_time)
        return self.rss_name

    class Meta:
        database = command_db
            

class Rss_Keyword(db.Model):
    rss = ForeignKeyField(Rss, related_name='keys')
    rss_keyword_type = CharField(verbose_name='Type')
    rss_keyword = CharField(verbose_name='Keyword')
    rss_keyword_rating = IntegerField(default=0, verbose_name='Rating')
    rss_keyword_hits = IntegerField(default=0, verbose_name='Hits')
    rss_keyword_desc = TextField(null=True, verbose_name='Description')
    
    def __unicode__(self):
        return 'rss:%s rss_keyword_type:%s rss_keyword:%s rss_keyword_desc:%s' % \
               (self.rss, self.rss_keyword_type, self.rss_keyword, self.rss_keyword_desc)

    class Meta:
        database = command_db

class Rss_Access(db.Model):
    rss = ForeignKeyField(Rss, related_name='access')
    rss_access_time = DateTimeField(default=datetime.now, verbose_name='Access Time')
    rss_access_result = BooleanField(default=False, verbose_name='Access Result')
    rss_access_count = IntegerField(default=0, verbose_name='Valid Count')


    def __unicode__(self):
        # return 'rss:%s rss_access_time:%s rss_access_result:%s rss_access_count:%s' % \
        #        (self.rss, self.rss_access_result, str(self.rss_access_time), self.rss_access_count)
        return str(self.id)

    class Meta:
        database = command_db


class Rss_Item(db.Model):
    rss_access = ForeignKeyField(Rss_Access, related_name='items')
    rss_item_title = CharField(verbose_name='Title')
    rss_item_desc = TextField()
    rss_item_category = CharField()
    rss_item_author = CharField()
    rss_item_link = CharField()
    rss_item_guid = CharField()
    rss_item_pub_date = DateTimeField(verbose_name='Pub Date')
    rss_item_extension = TextField()
    rss_item_rating = IntegerField(default=0, verbose_name='Rating')
    rss_item_status = CharField(verbose_name='Status')

    def size(self):
        dict_extension = cPickle.loads(str(self.rss_item_extension))
        csize = utils.convertSize(string.atoi(dict_extension['contentlength']))
        return Markup(csize)

    def download(self):
        dict_extension = cPickle.loads(str(self.rss_item_extension))
        magnet = dict_extension['magneturi']
        magnet_html = '<a href="' + magnet + '"> <img src="/static/magnet.png" /></a>'

        torrent = dict_extension['enclosure']
        torrent_html = '<a href="' + torrent + '" target="_blank"> <img src="/static/torrent.png" /></a>'

        link = self.rss_item_link
        link_html = '<a href="' + link + '" target="_blank"> <img src="/static/link.png" /></a>'
        return Markup(magnet_html + torrent_html + link_html)

    def __unicode__(self):
        return 'rss_access:%s rss_item_title:%s rss_item_desc:%s rss_item_category:%s \
                rss_item_author:%s rss_item_link:%s rss_item_guid:%s rss_item_pub_date:%s \
                rss_item_extension:%s rss_item_status:%s' \
                % (self.rss_access, self.rss_item_title, self.rss_item_desc, self.rss_item_category, \
                   self.rss_item_author, self.rss_item_link, self.rss_item_guid, str(self.rss_item_pub_date), \
                   self.rss_item_extension, self.rss_item_status)

    class Meta:
        database = command_db

class Actress(db.Model):
    actress_name = CharField(verbose_name='Name')
    actress_birthday = DateField(null=True, verbose_name='Birthday')
    actress_blood_type = CharField(null=True, verbose_name='Blood Type')
    actress_height = IntegerField(null=True, verbose_name='Height')
    actress_bra_size = CharField(null=True, verbose_name='Bra Size')
    actress_bust = IntegerField(null=True, verbose_name='Bust')
    actress_waist = IntegerField(null=True, verbose_name='Waist')
    actress_hips = IntegerField(null=True, verbose_name='Hips')
    actress_url = CharField()
    actress_last_time = DateField(verbose_name='Last Time')

    def __unicode__(self):
        return self.actress_name

    class Meta:
        database = command_db

class Movie(db.Model):
    movie_number = CharField(verbose_name='Number')
    movie_name = CharField(verbose_name='Name')
    movie_duration = CharField(verbose_name='Duration')
    movie_actress = TextField(verbose_name='Actress')
    movie_multi_a = IntegerField()
    movie_release_date = DateField(verbose_name='Release Date')
    movie_press = CharField(null=True, verbose_name='Press')
    movie_desc = TextField(null=True)
    movie_status = CharField(verbose_name='Status')
    movie_magnet_count = IntegerField(default=0, verbose_name='M Count')

    def __unicode__(self):
        return self.movie_number + ' ' + self.movie_name

    class Meta:
        database = command_db

class Magnet(db.Model):
    movie = ForeignKeyField(Movie, related_name='magnets')
    magnet_desc = CharField(verbose_name='Description')
    magnet_web_url = CharField()
    magnet_link = CharField()
    magnet_size = CharField(verbose_name='Size')
    magnet_size_number = FloatField()
    magnet_files_count = IntegerField()
    magnet_upload_date = DateField(verbose_name='Upload Date')
    magnet_create_time = DateTimeField(default=datetime.now, verbose_name='Create Time')

    def link(self):
        magnet = self.magnet_link
        magnet_html = '<a href="' + magnet + '"> <img src="/static/magnet.png" /></a>'

        return Markup(magnet_html)

    def __unicode__(self):
        return self.magnet_desc

    class Meta:
        database = command_db
        

class Error_History(db.Model):
    # error_id = PrimaryKeyField()
    error_module = CharField()
    error_time = DateTimeField(default=datetime.now)
    error_message = TextField()

    def __unicode__(self):
        return 'error_module:%s error_time:%s error_message:%s' % (self.error_module, self.error_time, self.error_message)

    class Meta:
        database = command_db

        


# class Relationship(db.Model):
#     from_user = ForeignKeyField(User, related_name='relationships')
#     to_user = ForeignKeyField(User, related_name='related_to')

#     def __unicode__(self):
#         return 'Relationship from %s to %s' % (self.from_user, self.to_user)


# class Message(db.Model):
#     user = ForeignKeyField(User)
#     content = TextField()
#     pub_date = DateTimeField(default=datetime.datetime.now)

#     def __unicode__(self):
#         return '%s: %s' % (self.user, self.content)


# class Note(db.Model):
#     user = ForeignKeyField(User)
#     message = TextField()
#     status = IntegerField(choices=((1, 'live'), (2, 'deleted')), null=True)
#     created_date = DateTimeField(default=datetime.datetime.now)

def create_tables():
    User.create_table(fail_silently=True)
    Rss.create_table(fail_silently=True)
    Rss_Keyword.create_table(fail_silently=True)
    Rss_Access.create_table(fail_silently=True)
    Rss_Item.create_table(fail_silently=True)
    Error_History.create_table(fail_silently=True)

    Actress.create_table(fail_silently=True)
    Movie.create_table(fail_silently=True)
    Magnet.create_table(fail_silently=True)

def create_admin():
    admin = User(username='admin', admin=True, active=True, email='admin@example.com')
    admin.set_password('admin')
    admin.save()
