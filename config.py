# config

# class Configuration(object):
#     DATABASE = {
#         'name': 'example.db',
#         'engine': 'peewee.SqliteDatabase',
#         'check_same_thread': False,
#     }
#     DEBUG = True
#     SECRET_KEY = 'shhhh'

class Configuration(object):
    DATABASE = {
        'name': 'res_auto',
        'engine': 'peewee.MySQLDatabase',
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'res_auto',
        'passwd': 'no1Knows',
    }
    DEBUG = True
    SECRET_KEY = 'shhhh'
