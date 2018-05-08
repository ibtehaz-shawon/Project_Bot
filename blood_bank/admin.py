from django.contrib import admin
from .models import UserInformation, UserStatus, ErrorLogger, DonationHistory, FlowController

# Register your models here.

admin.site.register(UserInformation)
admin.site.register(UserStatus)
admin.site.register(DonationHistory)
admin.site.register(ErrorLogger)
admin.site.register(FlowController)
