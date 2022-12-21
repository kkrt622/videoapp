from django.contrib import admin
from .models import Video, UserVideoSettings, User, AuthenticationCode

admin.site.register(User)
admin.site.register(Video)
admin.site.register(AuthenticationCode)
admin.site.register(UserVideoSettings)
