import datetime
from flask import request, redirect

from flask_peewee.admin import Admin, ModelAdmin, AdminPanel
from flask_peewee.filters import QueryFilter

from app import app, db
from auth import auth
from models import User, Rss, Rss_Keyword, Rss_Access, Rss_Item, Error_History


# class NotePanel(AdminPanel):
#     template_name = 'admin/notes.html'

#     def get_urls(self):
#         return (
#             ('/create/', self.create),
#         )

#     def create(self):
#         if request.method == 'POST':
#             if request.form.get('message'):
#                 Note.create(
#                     user=auth.get_logged_in_user(),
#                     message=request.form['message'],
#                 )
#         next = request.form.get('next') or self.dashboard_url()
#         return redirect(next)

#     def get_context(self):
#         return {
#             'note_list': Note.select().order_by(Note.created_date.desc()).paginate(1, 3)
#         }

# class UserStatsPanel(AdminPanel):
#     template_name = 'admin/user_stats.html'

#     def get_context(self):
#         last_week = datetime.datetime.now() - datetime.timedelta(days=7)
#         signups_this_week = User.select().where(User.join_date > last_week).count()
#         messages_this_week = Message.select().where(Message.pub_date > last_week).count()
#         return {
#             'signups': signups_this_week,
#             'messages': messages_this_week,
#         }

# class RssAccessPanel(AdminPanel):
#     template_name = 'admin/user_stats.html'

#     def get_context(self):
#         last_week = datetime.datetime.now() - datetime.timedelta(days=7)
#         signups_this_week = User.select().where(User.join_date > last_week).count()
#         messages_this_week = Message.select().where(Message.pub_date > last_week).count()
#         return {
#             'signups': signups_this_week,
#             'messages': messages_this_week,
#         }

# class RssItemPanel(AdminPanel):
#     template_name = 'admin/user_stats.html'

#     def get_context(self):
#         last_week = datetime.datetime.now() - datetime.timedelta(days=7)
#         signups_this_week = User.select().where(User.join_date > last_week).count()
#         messages_this_week = Message.select().where(Message.pub_date > last_week).count()
#         return {
#             'signups': signups_this_week,
#             'messages': messages_this_week,
#         }

# class ErrorHistoryPanel(AdminPanel):
#     template_name = 'admin/user_stats.html'

#     def get_context(self):
#         last_week = datetime.datetime.now() - datetime.timedelta(days=7)
#         signups_this_week = User.select().where(User.join_date > last_week).count()
#         messages_this_week = Message.select().where(Message.pub_date > last_week).count()
#         return {
#             'signups': signups_this_week,
#             'messages': messages_this_week,
#         }

admin = Admin(app, auth, branding='Res-Auto Site')


# class MessageAdmin(ModelAdmin):
#     columns = ('user', 'content', 'pub_date',)
#     foreign_key_lookups = {'user': 'username'}
#     filter_fields = ('user', 'content', 'pub_date', 'user__username')

# class NoteAdmin(ModelAdmin):
#     columns = ('user', 'message', 'created_date',)
#     exclude = ('created_date',)

class RssAdmin(ModelAdmin):
    paginate_by = 100
    columns = ('rss_name', 'rss_url', 'rss_desc', 'rss_last_time')
    filter_fields = ('rss_name')

class RssKeywordAdmin(ModelAdmin):
    paginate_by = 100
    columns = ('rss', 'rss_keyword_type', 'rss_keyword', 'rss_keyword_rating', 'rss_keyword_hits', 'rss_keyword_desc',)
    filter_fields = ('rss', 'rss_keyword_type', 'rss_keyword_rating', 'rss_keyword_hits')

class RssAccessAdmin(ModelAdmin):
    paginate_by = 100
    columns = ('rss', 'rss_access_result', 'rss_access_count', 'rss_access_time',)
    foreign_key_lookups = {'rss': 'rss_name'}
    filter_fields = ('rss', 'rss_access_result', 'rss_access_time')
    exclude = ('rss_access_time',)

class RssItemAdmin(ModelAdmin):
    paginate_by = 100
    columns = ('rss_item_title', 'download', 'size', 'rss_item_pub_date', 'rss_item_rating', 'rss_item_status',)
    filter_fields = ('rss_item_title', 'rss_item_pub_date', 'rss_item_rating', 'rss_item_status')

class ErrorHistoryAdmin(ModelAdmin):
    paginate_by = 100
    columns = ('error_module', 'error_time', 'error_message',)
    filter_fields = ('error_module', 'error_time')
    exclude = ('error_time',)

auth.register_admin(admin)
admin.register(Rss, RssAdmin)
admin.register(Rss_Keyword, RssKeywordAdmin)
admin.register(Rss_Access, RssAccessAdmin)
admin.register(Rss_Item, RssItemAdmin)
admin.register(Error_History, ErrorHistoryAdmin)
# admin.register(Relationship)
# admin.register(Message, MessageAdmin)
# admin.register(Note, NoteAdmin)
# admin.register_panel('Notes', NotePanel)
# admin.register_panel('User stats', UserStatsPanel)

# admin.register_panel('Rss Access', RssAccessPanel)
# admin.register_panel('Rss Items', RssItemPanel)
# admin.register_panel('Error History', ErrorHistoryPanel)
