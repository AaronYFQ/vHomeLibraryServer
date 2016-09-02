
from django.conf.urls import patterns, url
from book import views,vbook
from django.views.decorators.cache import cache_page


urlpatterns = patterns('',
#       user and shop
        url(r'^regist/$',views.regist,name = 'regist'),
        url(r'^login/$',views.login,name = 'login'),
        url(r'^postRegisterID/$',views.postRegisterID,name = 'postRegisterID'),
        url(r'^createShop/$',views.createShop, name = 'createShop'),
        url(r'^modifyShop/$',views.modifyShop, name = 'modifyShop'),
        url(r'^manageShop/$',views.manageShop, name = 'manageShop'),
        url(r'^browseShop/$',views.browseShop, name = 'browseShop'),
#       book
        url(r'^addBook/$',vbook.addBook, name = 'addBook'),
		url(r'^getBook/$',vbook.getBook, name = 'getBook'),
        url(r'^removeBook/$',vbook.removeBook, name = 'removeBook'),
        url(r'^getBorrowBook/$',vbook.reqBorrowBook, name = 'borrowBook'),
        url(r'^postBorrowAction/$',vbook.respBorrowAction, name = 'respBorrowBook'),
        url(r'^returnBook/$',vbook.returnBook, name = 'returnBook'),
        url(r'^getCurrentBorrowBook/$',vbook.getCurrentBorrowBook, name = 'currentBorrowBook'),
        url(r'^getHistoryBorrowBook/$',vbook.getHistoryBorrowBook, name = 'HistoryBorrowBook'),
#        url(r'^modifyBook/$',views.modifyBook, name = 'modifyBook'),
#        url(r'^delBook/$',views.delBook, name = 'delBook'),
#       search 
		url(r'^searchBook/$',vbook.searchBook, name = 'searchBook'),
		url(r'^searchArea/$',views.searchArea, name = 'searchArea'),
#       event
        url(r'^checkMessage/$',views.checkEventCnt, name = 'checkEventCnt'),
        url(r'^getMessage/$',views.getEventComment, name = 'getEventComment'),

)
