#-*- coding:utf-8 -*-  
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.forms.models import model_to_dict
from django.core.cache import cache
from book.models import *
from book.Util.upJiGuang import *
from book.Util.util import *
import simplejson
import random
import datetime
import logging
import sys, os

# Get an instance of a logger
#logger = logging.getLogger(__name__)
logger = logging.getLogger("mysite")

# Create your views here.
def regist(request):
    state = "fail"
    dict = {}
    
    logger.info(request.POST)
    logger.info(os.getpid())
    if request.method == 'POST':
        username = request.POST.get('username', '')		
        password = request.POST.get('password', '')
        #regid = request.POST.get('regid', '')
        #regid = "18071adc030bb6dd31d"

        if User.checkIsExistWithName(username):
            state = 'user_exist'
        else:
            User.createUserRow(username, password, username, "", "", username)
#            jpushResult = jpushDeviceSetAlias(regid, username)
    	    dict['token'] = username 
#            print "==========? " +  str(jpushResult)
#            dict['jpushResult'] = jpushResult
            state = 'success'

    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

def postRegisterID(request):
    state = "fail"
    dict = {}
    
    logger.info(request.POST)
    logger.info(os.getpid())
    if request.method == 'POST':
        token = request.POST.get('token', '')		
        regid = request.POST.get('regid', '')

        user = User.getUserWithToken(token)
        if user is None:
            state = 'token invalid'
        else:
            user.regid = regid 
            user.save()
            state = 'success'

    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)


def login(request):
    state = "fail"
    dict = {}
    dict['shopname'] = "" 

    logger.info(request.POST)
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        user = User.getUserWithNamePwd(username, password)
        if user is None:
            state = 'not_exist_or_password_error'        
        else:
            shops = User.getUserShops(user)
            if shops is not None and len(shops):
                fstShop = shops[0]
                dict['shopname'] = fstShop.name

            token = User.setUserToken(user)
            dict['token'] = token 
            state = 'success'

    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

       		
######################## S H O P #############################

def createShop(request):
    state = "fail"
    dict = {}

    logger.info(request.POST)
    if request.method == 'POST':
        token = request.POST.get('token', '')
        shopname = request.POST.get('shopname', '') 
        
        user = User.getUserWithToken(token)
        if user is None:
            state = 'user unknown'
        else:
            shops = User.getUserShops(user)
            flag = 0
            if shops is None:
                pass
            else:
                for shop in shops:
                    if shop.name == shopname:
                        flag = 1
                        state = 'have this shop in this user'
                        break

            if flag == 0: 
                addr = request.POST.get('shopaddr', '')
                comment = request.POST.get('shopcomment', '')
                shop = Shop.createShopRow(shopname, addr, comment, user.id, user.name, changeTag=0)
                user.Belong_user.add(shop)
                state = 'success'					        

    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

def manageShop(request):
    state = "fail"
    dict = {}

    logger.info(request.GET)
    if request.method == 'GET':
        token = request.GET.get('token', '')
        shopname = request.GET.get('shopname', '')
        if token and shopname:
            user = User.getUserWithToken(token)
            if user is None:
                state = 'user unknown'
            else:
                shop = Shop.getShopWithNameAndUser(shopname, user.id)
                if shop is None:
                    state = 'this shop not in '+user.name
                else:
                    shopVersion = shop.changeTag
                    cacheTag = request.get_full_path()
                    cacheKey = getCacheKey(cacheTag, key_prefix='shop', version=shopVersion)
                    cacheValue = cache.get(cacheKey, version=shopVersion)
#cacheValue = 0
                    if cacheValue:
                        json=simplejson.dumps(cacheValue)
                        return HttpResponse(json)
                    else:
                        books = shop.Belong_Shop.all();
                        dict['user'] = user.name
                        dict['shop'] = shop.name
                        booklist = []
                        for book in books:
                            booklist.append(model_to_dict(book)) 
                        dict['books'] = booklist
                        dict['result'] = 'success'
                        cacheKey = getCacheKey(cacheTag, key_prefix='shop', version=shopVersion)
                        cache.set(cacheKey, dict,  version=shopVersion)
                        state = 'success'
        else:
            state = "token or shopname NULL"
    
    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

def browseShop(request):
    state = "fail"
    dict = {}

    logger.info(request.GET)
    if request.method == 'GET':
        username = request.GET.get('user', '')
        shopname = request.GET.get('shopname', '')
	
        user = User.getUserWithName(name=username)	
        if user is None:
            state = 'user unknown'
        else:
            shop = Shop.getShopWithNameAndUser(shopname, user.id)
            if shop is None:
                state = 'this shop not in '+user.name
            else:
                books = shop.Belong_Shop.all();
                dict['user'] = user.name
                dict['shop'] = shop.name
                booklist = []
                for book in books:
                    booklist.append(model_to_dict(book)) 
                dict['books'] = booklist
                state = 'success'
    
    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)


def modifyShop(request):
    state = "fail" 
    dict = {}

    logger.info(request.POST)
    if request.method == 'POST':
        token = request.POST.get('token', '')
        oldname = request.POST.get('oldname', '')
        newname = request.POST.get('newname', '')

        user = User.getUserWithToken(token)
        if user is None:
            state = 'user unknown'
        else:
            shop = Shop.getShopWithNameAndUser(oldname, user.id)
            if shop is None:
                state = 'this shop not in '+user.name
            else:
                shop.name = newname
                shop.save()
                dict['shopname'] = newname
                state = 'success'
    
    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)


def searchArea(request):
    state = "fail"
    dict = {}
    
    logger.info(request.GET)
    if request.method == 'GET':
        shopaddr = request.GET.get('areaname', '')		
        shops = Shop.objects.filter(addr__contains=shopaddr)
        shoplist = []
        if shops.count():
            for shop in shops:
                bookcnt = shop.Belong_Shop.all().count();
                book_dict = model_to_dict(shop)
                book_dict['bookcnt'] = bookcnt
                shoplist.append(book_dict)
        dict['shops'] = shoplist
        state = 'success'

    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

def checkEventCnt(request):
    state = None
    dict = {}

    logger.info(request.GET)
    if request.method == 'GET':
        token = request.GET.get('token', '')
        try:
            user = User.objects.get(token=token)
        except:
            state = 'novalid token'
        else:        
            cnt = UserEvent.objects.filter(user_id=user.id).count()
            dict['count'] = cnt 
            state = 'success'

    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

def getEventComment(request):
    state = None
    dict = {}
    
    logger.info(request.GET)
    logger.info(os.getpid())
    if request.method == 'GET':
        token = request.GET.get('token', '')
        try:
            user = User.objects.get(token=token)
        except:
            state = 'novalid token'
        else:
            recv_msgs = UserEvent.objects.filter(user_id=user.id)
            cnt = recv_msgs.count()
            recv_msg_list = []
            if recv_msgs.count():
                for recv_msg in recv_msgs:
                    recv_msg_dict = model_to_dict(recv_msg)
                    recv_msg_list.append(recv_msg_dict)

            UserEvent.objects.filter(user_id=user.id).delete()
            dict['messages'] = recv_msg_list 
            dict['count'] = cnt 
            state = 'success'

    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

