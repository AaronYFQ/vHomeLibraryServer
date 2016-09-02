from django.db import models
# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=30)
    pwd = models.CharField(max_length=30)
    
    @classmethod
    def createUserRow(self, username, passward):
        User.objects.create(name=username,pwd=passward)

    def __unicode__(self):
        return self.name

