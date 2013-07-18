#!/usr/bin/python
# -*- coding: utf-8 -*-

import feedparser
import cPickle

from models import *

def parseKickAssDotTo(item):
    torrent = {}
    torrent['contentlength'] = item.get('torrent_contentlength', 'res_auto_unknown')
    torrent['infohash'] = item.get('torrent_infohash', 'res_auto_unknown')
    torrent['magneturi'] = item.get('torrent_magneturi', 'res_auto_unknown')
    torrent['filename'] = item.get('torrent_filename', 'res_auto_unknown')
    torrent['enclosure'] = item.enclosures[0].href

    return cPickle.dumps(torrent)

def calculateRating(rks, title):
    rating = 0

    for rk in rks:
        allmatch = True
        for singlekey in rk.rss_keyword.split(' '):
            if not singlekey in title.lower():
                allmatch = False
        if allmatch == True:
            rk.rss_keyword_hits += 1
            rating += rk.rss_keyword_rating
            rk.save()

    return rating

def insertRssItem(rss, ra, rks, item, time):
    tuple_time = item.get('published_parsed')
    date_time= datetime(*tuple_time[0:6])

    if date_time <= time:
        return False

    ri = Rss_Item()
    ri.rss_access = ra
    ri.rss_item_title = item.get('title', u'res_auto_unknown')
    ri.rss_item_desc = item.get('description', u'res_auto_unknown')
    ri.rss_item_category = item.get('category', u'res_auto_unknown')
    ri.rss_item_author = item.get('author', u'res_auto_unknown')
    ri.rss_item_link = item.get('link', u'res_auto_unknown')
    ri.rss_item_guid = item.get('guid', u'res_auto_unknown')
    ri.rss_item_pub_date = date_time
    
    if rss.rss_name == 'kickass.to':
        ri.rss_item_extension = parseKickAssDotTo(item)
    else:
        ri.rss_item_extension = u'res_auto_unknown'
    
    ri.rss_item_rating = calculateRating(rks, ri.rss_item_title)
    if ri.rss_item_rating == 0:
        ri.rss_item_status = u'skipped'
    else:
        ri.rss_item_status = u'pending'

    ri.save()

    if date_time > rss.rss_last_time:
        rss.rss_last_time = date_time

    return True

def processRssFeed(rss):
    ra = Rss_Access.create(rss=rss)

    rks = Rss_Keyword.select().where(Rss_Keyword.rss == rss)

    result = feedparser.parse(rss.rss_url)

    index = 0
    valid_count = 0
    parse_count = len(result.entries)
    time = rss.rss_last_time
    while index < parse_count:
        item = result.entries[parse_count - index - 1]
        if insertRssItem(rss, ra, rks, item, time) == True:
            valid_count+=1
        index += 1

    if valid_count > 0:
        rss.save()

    ra.rss_access_result = True
    ra.rss_access_count = valid_count

    ra.save()

def main():
    for rss in Rss.select():
        processRssFeed(rss)

if __name__ == '__main__':
    main()
