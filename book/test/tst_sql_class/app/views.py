#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, render_to_response
from app.models import User
import simplejson
# Create your views here.

def regist(request):
    state = "fail"
    dict = {}
    print "Hello world"
    if request.method == 'GET':
        username = request.GET.get('username', '')
        password = request.GET.get('password', '')
        User.createUserRow(username, password)
        state = "success"
    
    dict['result'] = state
    json=simplejson.dumps(dict)
    return HttpResponse(json)

