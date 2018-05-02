from __future__ import unicode_literals
from django.db import models

"""
python manage.py makemigrations App_Name
python manage.py sqlmigrate App_Name Migration_Number (check migrations folder)
python manage.py migrate
"""

# this is just to dump incoming ALL messages and when the message has been received

"""
This table is to be used for testing purpose and probably data dumping purpose; if needed ever;
"""


class DataDump(models.Model):
    incomingText = models.CharField(max_length = 10000)
    userID = models.CharField(max_length = 100)
    recordedTime = models.DateTimeField('date recorded')
    confidenceBye = models.DecimalField(null=True, max_digits=21, decimal_places=18)
    confidenceGreet = models.DecimalField(null=True, max_digits=21, decimal_places=18)
    confidenceLoc = models.DecimalField(null=True, max_digits=21, decimal_places=18)
    confidenceThank = models.DecimalField(null=True, max_digits=21, decimal_places=18)
    messageType = models.CharField(max_length=10, null=True)


"""
UserTable contains all the necessary information needed for a particular user.
donorID is the facebook user id sent by facebook; it's unique from facebook
userID is the unique id (UUID4()) generated from the app and will act as primary identifier across the app
mobileVerification process is not fixed. might change later.
"""


class UserTable(models.Model):
    userID = models.CharField(max_length=50, unique=True, primary_key=True)
    facebookUserID = models.CharField(max_length=100, unique=True)
    bloodGroup = models.CharField(max_length=2, null=True, default=None, blank=True)
    mobileNumber = models.CharField(max_length=15, unique=False, null=True, default=-1)
    mobileVerified = models.BooleanField(default=False)
    homeCity = models.CharField(max_length=50, null=True, default=-1)
    currentCity = models.CharField(max_length=50, null=True, default=-1)


"""
donationHistory table contains every history of a particular user.
userID comes from the userTable and is unique. This table has a 1:M relation with UserTable
"""


class DonationHistory(models.Model):
    userID = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    donatedOn = models.CharField(max_length=30, null=True, default=-1)


"""
UserStatus contains the current status of this user in particular situation.
userID comes from the userTable and is unique. This table has a 1:M relation with UserTable
other statuses are basically boolean. This table might change later.
"""


class UserStatus(models.Model):
    userID = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    freshUser = models.BooleanField(default=True)
    getStartedStatus = models.BooleanField(default=False, blank=True)
    donationStatus = models.BooleanField(default=False, blank=True)
    informationStatus = models.BooleanField(default=False, blank=True)
    donationAvailDate = models.DateField(blank=True, null=True)


"""
ErrorLog is the default error handler for this app.
userID comes from the userTable and is unique. This table has a 1:M relation with UserTable
"""


class ErrorLogger(models.Model):
    instanceNumber = models.CharField(max_length=64, primary_key=True, unique=True)
    errorCounter = models.IntegerField(null=False, default=-1)
    userID = models.CharField(max_length=100, null=True, default="no_user_id")
    errorPlace = models.CharField(max_length=100, null=False, default='dummy!')
    errorMessage = models.CharField(max_length=1000, null=True, default='unknown error!')
    recordedTime = models.DateTimeField(auto_now_add=True, blank=True)
    errorCode = models.IntegerField(default=-1, blank=True, null=True)
    errorSubCode = models.IntegerField(default=-1, blank=True, null=True)
    errorType = models.CharField(default=None, max_length=1000, blank=True, null=True)
