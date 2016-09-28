#coding = utf-8
'''
This function of this file:
1. modify the alias or tags of device
2. push message by registerId or alise or tags
3. adopt celery Using an asyncchronous manner to push message by share_task
    for the detailed info: please read the link below:
        http://www.jianshu.com/p/1840035cb510 
        http://shangliuyan.github.io/2015/07/04/celery%E6%9C%89%E4%BB%80%E4%B9%88%E9%9A%BE%E7%90%86%E8%A7%A3%E7%9A%84/
'''

from __future__ import absolute_import
from .conf import app_key, master_secret
from celery import shared_task
from jpush import common
import jpush as jpush
#regid = "18071adc030bb6dd31d"


def jpushCreateDevice():
    _jpush = jpush.JPush(app_key, master_secret)
    device = _jpush.create_device()
    _jpush.set_logging("DEBUG")
    
    return device

@shared_task
def add(x, y):
    return x+y

@shared_task
def jpushDeviceSetAlias(regid, alias):
    device = jpushCreateDevice()
    entity = jpush.device_alias(alias)
    result = device.set_devicemobile(regid, entity)
    return result.status_code

@shared_task
def jpushDeviceClearAlias(regid, alias):
    device = jpushCreateDevice()
    entity = jpush.device_alias("")
    result = device.set_deviceinfo(regid, entity)
    return result.status_code

@shared_task
def jpushDeviceSetTag(regid, tags):
    device = jpushCreateDevice()
    entity = jpush.device_tag(jpush.add(tags))
    result = device.set_devicemobile(regid, entity)
    return result.status_code

@shared_task
def jpushDeviceSetTag(regid, tags):
    device = jpushCreateDevice()
    entity = jpush.device_tag("")
    result = device.set_deviceinfo(regid, entity)
    return result.status_code

@shared_task
def jpushDeviceSetAliasAndTag(regid, tags, alias):
    result1 = jpushDeviceSetAlias(regid, alias)
    result2 = jpushDeviceSetTag(regid, tags)

    return result1 and result2

''' push operation '''

@shared_task
def jpushCreateClient():
    _jpush = jpush.JPush(app_key, master_secret)
    push = _jpush.create_push()
    push.platform = jpush.all_

    return push

@shared_task
def jushPushMessageToJiGuang(push):
    try:
        response=push.send()
    except common.Unauthorized:
        raise common.Unauthorized("Unauthorized")
    except common.APIConnectionException:
        raise common.APIConnectionException("conn")
    except common.JPushFailure:
        print ("JPushFailure")
    except:
        print ("Exception")

    return response

@shared_task
def jpushMessageWithRegId(regid, msg, action):
    push = jpushCreateClient()
    push.audience = jpush.audience(
            jpush.registration_id(regid)
        )
    push.notification = jpush.notification(android=jpush.android(alert=action, extras=msg))
    print msg, push.notification
    resp = jushPushMessageToJiGuang(push)
    return resp

@shared_task
def jpushMessageWithTags(tags, msg, action):
    push = jpushCreateClient()
    push.audience = jpush.audience(
            jpush.tag(tags)
        )
    push.notification = jpush.notification(android=jpush.android(alert=action, extras=msg))
    resp = jushPushMessageToJiGuang(push)
    return resp


@shared_task
def jpushMessageWithAlias(alias, msg, action):
    push = jpushCreateClient()
    push.audience = jpush.audience(
            jpush.alias(alias)
        )
    push.notification = jpush.notification(android=jpush.android(alert=action, extras=msg))
    resp = jushPushMessageToJiGuang(push)
    return resp

@shared_task
def jpushMessageWithAliasTag(alias, tags, msg, action):
    print "xxx"
    push = jpushCreateClient()
    push.audience = jpush.audience(
            jpush.alias(alias),
            jpush.tag(tags)
            )
    push.notification = jpush.notification(android=jpush.android(alert=action, extras=msg))
    resp = jushPushMessageToJiGuang(push)
    return resp

@shared_task
def jpushMessageAllUser(action, msg):
    push = jpushCreateClient()
    push.audience = jpush.all_
    push.notification = jpush.notification(android=jpush.android(alert=action, extras=msg))
    resp = jushPushMessageToJiGuang(push)
    return resp


if __name__ == '__main__':
#jpushDeviceSetAlias(regid, "xxx")
    print jpushMessageAllUser('hello', {"112":"www"})
    print jpushMessageWithRegId("1507bfd3f7cf3e96363", {}, "hello")
