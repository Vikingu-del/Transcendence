from django.contrib import admin
from chat.models import ChatModel, UserProfileModel, ChatNotification
# Register your models here.
admin.site.register(ChatModel)
admin.site.register(UserProfileModel)
admin.site.register(ChatNotification)