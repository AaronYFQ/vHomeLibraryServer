# coding=utf-8   #默认编码格式为utf-8 
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.forms.models import model_to_dict

from book.models import *
#from book.Util.upJiGuang import *
from book.Util.tasks import *
from book.Util.util import *
import simplejson
import random
import datetime
import logging
import sys
#logger = logging.getLogger(__name__)
logger = logging.getLogger("mysite")

'''
function: get current time
return: Time
Notice: none
'''
def getCurrentTime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

'''
function: record footprint of borrowing book
return: none
Notice: please sync the status of APP
'''
def recordToHistory(user, book_dict):
    if book_dict['action'] == 'borrow':
        if UserCurrentBorrow.checkIsExistThisBook(user.id, book_dict['owner'], book_dict['shop'], book_dict['book'], "borrowing"):
            pass
        else:
            UserCurrentBorrow.createUserCurrentBorrow(user.id, book_dict['owner'], book_dict['shop'], book_dict['book'], "borrowing", book_dict['time'], "", "")

    elif book_dict['action'] == 'accept':
        borrowBook = UserCurrentBorrow.getThisBorrowBook(user.id, book_dict['owner'], book_dict['shop'], book_dict['book'], "borrowing")
        if borrowBook is None:
            logger.info("resp borrow exception")
        else:
            borrowBook.accepttime = book_dict['time']
            borrowBook.state = "borrow"
            borrowBook.save()
        
    elif book_dict['action'] == 'refuse':
        borrowBook = UserCurrentBorrow.getThisBorrowBook(user.id, book_dict['owner'], book_dict['shop'], book_dict['book'], "borrowing")
        if borrowBook is None:
            logger.info("resp borrow exception")
        else:
            borrowBook.accepttime = book_dict['time']
            borrowBook.state = "borrow"
            borrowBook.save()
 
    elif book_dict['action'] == 'return':
        borrowBook = UserCurrentBorrow.getThisBorrowBook(user.id, book_dict['owner'], book_dict['shop'], book_dict['book'], "borrow")
        if borrowBook is None:
            logger.info("return exception")
        else:
            borrowBook.finishtime = book_dict['time']
            borrowBook.state = "finish"
            borrowBook.save()
    else:
        logger.info("no this action")

######################## B O O K #############################	
'''
function: add book to database
return: states
Notice：invalid cache of shop
'''
def addBook(request):
    state = "fail" 
    dict = {}

    logger.info(request.POST)
    if request.method == 'POST':
        token = request.POST.get('token', '')
        shopname = request.POST.get('shopname', '')
        bookname = request.POST.get('bookname', '') 
        bookNum = request.POST.get('booknum', '')
        
       
        user = User.getUserWithToken(token)
        if user is None:
            state = 'invalid token'
        else:
            shop = Shop.getShopWithNameAndUser(shopname, user.id)
            if shop is None:
                state = 'invalid user shop name'
            else:
                if Book.checkIsExistWithName(shop, bookname):
                    book = Book.objects.get(name=bookname, shop_id=shop.id)
                    print book
                    newNum = int(book.bookNum) + int(bookNum)
                    newAvail = int(book.availNum) + int(bookNum)
                    print book.bookNum,newNum,newAvail
                    Book.objects.filter(name=bookname,shop_id=shop.id).update(bookNum = newNum,availNum = newAvail )
                    state = 'success'     
                    shop.changeTag +=1
                    shop.save()
                else:
                    author = request.POST.get('bookauthor', '')
                    publisher = request.POST.get('bookpublisher', '')
                    detail = request.POST.get('bookcomments', '')
                    isbn = request.POST.get('bookisbn', '')
                    imageurl = request.POST.get('imageurl', '')
                    extlink = request.POST.get('extlink', '')
                    availNum = int(bookNum) 

                    book = Book.createBookRow(bookname, author, publisher, detail, shop.id, 1, isbn, "", imageurl, extlink, bookNum, availNum)
                    # Mr Yang delete below line, why?
					#shop.Belong_Shop.add(book)
                    shop.changeTag += 1 # to invalid cache
                    shop.save()
                    state = 'success'

    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

'''
function: get book
return: state and the detailed info about book
notice: none
'''
def getBook(request):
    state = "fail"
    dict = {}
    
    logger.info(request.GET)
    if request.method == "GET":
        shopuser = request.GET.get('shopuser', '')
        shopname = request.GET.get('shopname', '')
        bookname = request.GET.get('bookname', '') 

        user = User.getUserWithName(shopuser)
        if user is None:
            state = 'invalid shopuser'
        else:
            shop = Shop.getShopWithNameAndUser(shopname, user.id)
            if shop is None:
                state = 'invalid user shop name'
            else:
                book = Book.getBookWithName(bookname, shop.id)
                dict['book'] = model_to_dict(book)
                state = 'success'
            
    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

'''
function: delete book from database
return: state
notice: invalid cache
'''
def removeBook(request):
    state = "fail" 
    dict = {}
    
    logger.info(request.POST)
    if request.method == "POST":
        token = request.POST.get('token', '')
        shopname = request.POST.get('shopname', '')
        bookname = request.POST.get('bookname', '') 
        delBookNum = request.POST.get('booknum','')

        user = User.getUserWithToken(token)
        if user is None:
            state = 'invalid token'
        else:
            shop = Shop.getShopWithNameAndUser(shopname, user.id)
            if shop is None:
                state = 'no have this shop in your'
            else:
                book = Book.objects.get(name=bookname, shop_id=shop.id)
                print book
                newNum = int(book.bookNum) - int(delBookNum)
                newAvail = int(book.availNum) - int(delBookNum)
                print book.bookNum, newNum, newAvail
                if newNum == 0:
                    Book.objects.filter(name=bookname, shop_id=shop.id).delete()
                else:
                    Book.objects.filter(name=bookname, shop_id=shop.id).update(bookNum=newNum, availNum=newAvail)
                shop.changeTag += 1
                shop.save()
                state = 'success'
            
    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

'''
function: request to borrow book 
return: state
Notice: jpush 
'''
def reqBorrowBook(request):
    state = "fail" 
    dict = {}
    
    logger.info(request.GET)
    if request.method == "GET":
        shopuser = request.GET.get('shopuser', '')
        token = request.GET.get('token', '')
        shopname = request.GET.get('shopname', '')
        bookname = request.GET.get('bookname', '') 
 
        owner = User.getUserWithName(shopuser)
        borrower = User.getUserWithToken(token)
        if owner is None and borrower is None:
            state = 'novalid token'
        else:        
            shop = Shop.getShopWithNameAndUser(shopname, owner.id)
            if shop is None:
                state = 'no have this shop in your'
            else:
                book = Book.getBookWithName(bookname, shop.id)
                curtime = getCurrentTime()
                msgBook = {}
                msg = {}
                action = "borrow"
                msgBook['owner'] = owner.name
                msgBook['shop'] = shopname  # notice hongfei
                msgBook['book'] = bookname
                msgBook['borrower'] = borrower.name
                msgBook['time'] = curtime
                msgBook['action'] = action
                msgList = []
                msgList.append(msgBook)
                msg['messages'] =msgList 
                msg['count'] = 1
                alert =  borrower.name + u'  向你借书： <<'.encode('utf-8').decode('utf-8') + bookname + ">>"
                logger.info(bookname)
                logger.info(alert)
                jpushMessageWithRegId.delay(owner.regid, msg, alert); # push message
                    #userEvent = UserEvent.objects.create(user_id=owner.id, owner=owner.name, borrower=borrower.name, \
                    #        book=bookname, time=curtime, shop=shopname, action="borrow")
#recordToHistory(borrower, model_to_dict(userEvent))
                 
                recordToHistory(borrower, {'owner':owner.name,'shop':shopname, 'book':bookname, 'action':action, 'time':curtime})
                state = 'success'
            
    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

'''
function:  response about borrowing request -- accept or refuse
return: state
notice: jpush
'''
def respBorrowAction(request):
    state = "fail"
    dict = {}
    
    logger.info(request.POST)
    if request.method == "POST":
        token = request.POST.get('token', '')
        fromname = request.POST.get('borrower', '')
        shopname = request.POST.get('shopname', '')
        bookname = request.POST.get('bookname', '') 
        action = request.POST.get('action', '') 
 
        borrower = User.getUserWithName(fromname)
        owner = User.getUserWithToken(token)
        if owner is None and borrow is None:
            state = 'novalid token'
        else:        
            shop = Shop.getShopWithNameAndUser(shopname, owner.id)
            if shop is None:
                state = 'no have this shop in your'
            else:
                book = Book.getBookWithName(bookname, shop.id)
                if book.availNum <= 0:
                    state = 'no available book'
                else:
                    curtime = getCurrentTime()
                    msg = {}
                    msgBook = {}
                    msgBook['owner'] = owner.name
                    msgBook['shop'] = shopname
                    msgBook['book'] = bookname
                    msgBook['borrower'] = borrower.name
                    msgBook['time'] = curtime
                    msgBook['action'] = action
                    msgList = []
                    msgList.append(msgBook)
                    msg['messages'] =msgList
                    msg['count'] = 1
#alert =  owner.name + u'  同意借书请求'.encode('utf-8').decode('utf-8')
                    alert =  owner.name + u'  同意借书： <<'.encode('utf-8').decode('utf-8') + bookname + ">>"
                    jpushMessageWithRegId.delay(borrower.regid, msg, alert);
                    #userEvent = UserEvent.objects.create(user_id=borrower.id, owner=owner.name, borrower=fromname, book=bookname, time=curtime, shop=shopname, action=action)
#recordToHistory(borrower, model_to_dict(userEvent))
                    recordToHistory(borrower, {'owner':owner.name,'shop':shopname, 'book':bookname, 'action':action, 'time':curtime})
                    if action == "accept":
                        if book.borrower == "":
                            book.borrower = fromname
                        else:
                            book.borrower += ","+fromname

                        book.availNum -= 1
                        if book.availNum <= 0:
                            book.state = 0
                    book.save()
                    shop.changeTag += 1
                    shop.save()

                    state = 'success'
            
    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

''' 
function: return book by owner
return: status
notice: not communicate with borrower
        invalid cache
'''
def returnBook(request):
    state = "fail"
    dict = {}
    
    logger.info(request.POST)
    if request.method == "POST":
        token = request.POST.get('token', '')
        shopname = request.POST.get('shopname', '')
        bookname = request.POST.get('bookname', '') 
        borrowArray = request.POST.get('borrows','').split(',')
        action = "return"#request.POST.get('action', '') 
 
        owner = User.getUserWithToken(token)
        if owner is None:
            state = 'invalid token'
        else:
            shop = Shop.getShopWithNameAndUser(shopname, owner.id)
            if shop is None:
                state = 'no have this shop in your'
            else:
                book = Book.getBookWithName(bookname, shop.id)
                if book is None: 
                    state = 'no have this book'
                else:
                    for borr in borrowArray:
                        borrower = User.getUserWithName(borr)
                        if borrower is None:
                            state = "borrower no exist"
                        else:
                            curtime = getCurrentTime() 
                            recordToHistory(borrower, {'owner':owner.name,'shop':shopname, 'book':bookname, 'action':action, 'time':curtime})
                            book.state = 1
                            book.borrower = book.borrower.replace(borrower.name, "", 1)
                            book.borrower = book.borrower.replace(",,", ",")
                            if book.borrower.find(',') == 0 :
                                book.borrower = book.borrower[1:]
                            book.availNum += 1
                            print book.borrower ,book.availNum
                        book.save()
                        shop.changeTag += 1
                        shop.save()

                        state = 'success'
            
    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

''' 
function: search book by name
return：booklist 
notice: none
'''
def searchBook(request):
    state = None
    dict = {}

    logger.info(request.GET)
    if request.method == 'GET':
        bookname = request.GET.get('bookname', '')		
        if bookname == "*":
            books = Book.objects.all()
        else:
            books = Book.objects.filter(name__contains=bookname);
        if books.count():
            booklist = []
            for book in books:
                book_dict = model_to_dict(book)
                shop = Shop.objects.get(id=book.shop_id) 
                user = User.objects.get(id=shop.user_id) 
                book_dict['shopname'] = shop.name
                book_dict['shopaddr'] = shop.addr
                book_dict['username'] = user.name
                booklist.append(book_dict)
            dict['books'] = booklist
            state = 'success'

    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

'''
function: get history of borrowing book
return: booklist that were borrowing
Notice: none
'''
def getCurrentBorrowBook(request):
    state = "fail"
    dict = {}

    logger.info(request.GET)
    if request.method == 'GET':
        token = request.GET.get('token', '')
        user = User.getUserWithToken(token)
        if user is None:
            state = 'invalid token'
        else:
            userCurBorrows = UserCurrentBorrow.objects.filter(user_id=user.id).filter(state__contains="borrow")
            userCurBorrowList = []

            for userCurBorrow in userCurBorrows:
                userCurBorrowList.append(model_to_dict(userCurBorrow)) 

            dict['books'] = userCurBorrowList 
            state = 'success'
    
    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

'''
function: get history of borrowed book
return: booklist that were borrowed
Notice: none
'''
def getHistoryBorrowBook(request):
    state = "fail"
    dict = {}

    logger.info(request.GET)
    if request.method == 'GET':
        token = request.GET.get('token', '')
	
        user = User.getUserWithToken(token)
        if user is None:
            state = 'invalid token'
        else:
            userCurBorrows = UserCurrentBorrow.objects.filter(user_id=user.id).filter(state__contains="finish")
            userCurBorrowList = []
            for userCurBorrow in userCurBorrows:
                userCurBorrowList.append(model_to_dict(userCurBorrow)) 
            dict['books'] = userCurBorrowList 
            state = 'success'
    
    dict['result'] = state
    json=simplejson.dumps(dict)
    logger.info(dict)
    return HttpResponse(json)

