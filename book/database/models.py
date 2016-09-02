from django.db import models
import random
class User(models.Model):
    name = models.CharField(max_length=30)
    pwd = models.CharField(max_length=30)
    token = models.CharField(max_length=30)
    regid = models.CharField(max_length=50)
    alias = models.CharField(max_length=50)
    tag = models.CharField(max_length=50)
    
    @classmethod
    def createUserRow(self, username, password, token, regid, tag, alias):
        User.objects.create(name= username, pwd=password, token=username, regid=regid, tag=tag, alias=alias)

    @classmethod
    def checkIsExistWithName(self, name):
        User.objects.filter(name=name).count() > 0

    @classmethod
    def getUserWithNamePwd(self, name, pwd):
        try:
            user = User.objects.get(name=name, pwd=pwd)
        except:
            return None
        else:
            return user
    
    @classmethod
    def getUserWithName(self, name):
        try:
            user = User.objects.get(name=name)
        except:
            return None
        else:
            return user

    @classmethod
    def getUserExistWithNameToken(self, token):
        try:
            user = User.objects.get(token)
        except:
            return None
        else:
            return user

    @classmethod
    def getUserShops(self, user):
        user.Belong_user.all()

    @classmethod
    def setUserToken(self, user):
        newtoken = "".join(random.sample('abcdefghijklmnopqrstuvwxyz',5))
        user.token = user.name + newtoken
        user.save()

    @classmethod
    def checkIsExistWithToken(self, token):
        User.objects.filter(token, token).count() > 0

    @classmethod
    def removeUserRow(self):
        pass

    @classmethod
    def updateUserRow(self):
        pass

    def __unicode__(self):
        return self.name

class Shop(models.Model):
    user = models.ForeignKey(User, related_name='Belong_user')
    name = models.CharField(max_length=30)
    addr = models.CharField(max_length=50)
    comment = models.TextField()
    
    username = models.CharField(max_length = 30)
    changeTag = models.IntegerField()

    @classmethod
    def createShopRow(self, shopname, addr, comment, userId, username, changeTag):
        Shop.objects.create(name=shopname, addr=addr, comment=comment, user_id=userId, username=username, changeTag=changeTag)

    @classmethod
    def getShopWithNameAndUser(self, name, userId):
        try:
            shop = Shop.objects.get(name=shopname, user_id=user.id)
        except:
            return None
        else:
            return shop

    def __unicode__(self):
        return self.name

class Book(models.Model):
    shop = models.ForeignKey(Shop, related_name='Belong_Shop')
    name = models.CharField(max_length=128)
    author = models.CharField(max_length=30)
    publisher = models.CharField(max_length=30)
    isbn  = models.CharField(max_length=128)
    detail = models.TextField()
    state = models.BooleanField()
    borrower  = models.CharField(max_length=128)
    imageurl = models.CharField(max_length = 128)
    extlink = models.CharField(max_length = 128)
   
    @classmethod
    def createBookRow(self, bookname, author, publisher, detail, shopid, state, isbn, borrower, imageurl, extlink):
        Book.objects.create(name=bookname, author=author, publisher=publisher, detail=detail, shop_id=shopid, state=state,\
                            isbn=isbn, borrower=borrower, imageurl=imageurl, extlink=extlink)
        return book

    @classmethod
    def getBookWithName(self, bookname, shopId):
        try:
            book = Book.objects.get(name=bookname, shop_id=shopId)
        except:
            return None
        else:
            return book
            

    @classmethod
    def checkIsExistWithName(self, shop, bookname):
        books = shop.Belong_Shop.all()
        for book in books:
            if bookname == book.name:
                return True
        return False

    def __unicode__(self):
        return self.name

class UserEvent(models.Model):
    user = models.ForeignKey(User, related_name='Userevent_user')
    owner = models.CharField(max_length=100)
    book = models.CharField(max_length=100)
    borrower = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    shop = models.CharField(max_length=100)
    action = models.CharField(max_length=200)

    def __unicode__(self):
        return self.owner + self.borrower

class UserAttentionShop(models.Model):
    user = models.ForeignKey(User, related_name='UAS_user')
    shopuser = models.CharField(max_length = 100)
    shopname = models.CharField(max_length = 100)

class UserAttentionBook(models.Model):
    user = models.ForeignKey(User, related_name='UAB_user')
    shopuser = models.CharField(max_length = 100)
    shopname = models.CharField(max_length = 100)
    bookname = models.CharField(max_length = 100)


class UserCurrentBorrow(models.Model):
    user = models.ForeignKey(User, related_name='UCB_user')
    owner = models.CharField(max_length=100)
    shop = models.CharField(max_length=100)
    book = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    starttime = models.CharField(max_length=100)
    accepttime = models.CharField(max_length=100)
    finishtime = models.CharField(max_length=100)

    def __unicode__(self):
        return self.shop + self.book 
