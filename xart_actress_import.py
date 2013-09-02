#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib2
import socket
import httplib
from htmlparser import XartActressList

from models import *

def recordError(module, message, detail):
    error = Error_History()
    error.error_module = module
    error.error_message = message
    error.error_detail = detail
    error.save()

def importActress():

    try:

        usock = urllib2.urlopen('http://x-art.com/models', timeout=120)
        parser = XartActressList()
        parser.feed(usock.read())
        usock.close()
        parser.close()

        index = 0
        actress_count = len(parser.actresses)
        while index < actress_count:
            actress = parser.actresses[actress_count - index - 1]
            exist_actresses = L_XART_Actress.select().where(L_XART_Actress.name == actress.name)
            if exist_actresses.count() == 0:
                actress.save()
                # print('[real] importing actress: ' + actress.name)
            else:
                print('        unique warning: ' + actress.name)

            index += 1

        # if last_time != actress.actress_last_time:
        #     actress.actress_last_time = last_time
        #     actress.save()
    except urllib2.HTTPError, e:
        recordError('XART_ACTRESS_IMPORT', str(e), 'NO MESSAGE')
        print e
    except urllib2.URLError, e:
        recordError('XART_ACTRESS_IMPORT', str(e), 'NO MESSAGE')
        print e
    except socket.timeout, e:
        recordError('XART_ACTRESS_IMPORT', str(e), 'NO MESSAGE')
        print e
    except socket.error, e:
        recordError('XART_ACTRESS_IMPORT', str(e), 'NO MESSAGE')
        print e
    except httplib.BadStatusLine, e:
        recordError('XART_ACTRESS_IMPORT', str(e), 'NO MESSAGE')
        print e
    # finally:
    #     if not usock is None:
    #         usock.close()
    #     if not parser is None:
    #         parser.close()

def main():
    # actresses = []

    # if len(sys.argv) == 1:
    #     actresses = Actress.select()
    # elif len(sys.argv) == 2:
    #     actresses = Actress.select().where(Actress.actress_name == sys.argv[1].decode('utf-8'))

    # for actress in actresses:
    #     print('begin to process actress: ' + actress.actress_name)
    #     processActress(actress)
    #     # print('end process actress:' + actress.actress_name)

    print('begin to import x-art actress: ')
    importActress()

if __name__ == '__main__':
    main()