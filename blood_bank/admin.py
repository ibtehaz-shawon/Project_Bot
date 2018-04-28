from django.contrib import admin
from .models import UserTable,UserStatus,ErrorLog,DonationHistory


# Register your models here.


admin.site.register(UserTable)
admin.site.register(UserStatus)
admin.site.register(DonationHistory)
admin.site.register(ErrorLog)
