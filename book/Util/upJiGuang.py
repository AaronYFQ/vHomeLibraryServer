#coding = utf-8
from conf import app_key, master_secret
import jpush as jpush
from jpush import common
regid = "18071adc030bb6dd31d"
def jpushCreateDevice():
    _jpush = jpush.JPush(app_key, master_secret)
    device = _jpush.create_device()
    _jpush.set_logging("DEBUG")
    
    return device

def jpushDeviceSetAlias(regid, alias):
    device = jpushCreateDevice()
    entity = jpush.device_alias(alias)
    result = device.set_devicemobile(regid, entity)
    return result.status_code

def jpushDeviceClearAlias(regid, alias):
    device = jpushCreateDevice()
    entity = jpush.device_alias("")
    result = device.set_deviceinfo(regid, entity)
    return result.status_code

def jpushDeviceSetTag(regid, tags):
    device = jpushCreateDevice()
    entity = jpush.device_tag(jpush.add(tags))
    result = device.set_devicemobile(regid, entity)
    return result.status_code

def jpushDeviceSetTag(regid, tags):
    device = jpushCreateDevice()
    entity = jpush.device_tag("")
    result = device.set_deviceinfo(regid, entity)
    return result.status_code

def jpushDeviceSetAliasAndTag(regid, tags, alias):
    result1 = jpushDeviceSetAlias(regid, alias)
    result2 = jpushDeviceSetTag(regid, tags)

    return result1 and result2

''' push operation '''
def jpushCreateClient():
    _jpush = jpush.JPush(app_key, master_secret)
    push = _jpush.create_push()
    push.platform = jpush.all_

    return push

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

def jpushMessageWithRegId(regid, msg, action):
    push = jpushCreateClient()
    push.audience = jpush.audience(
            jpush.registration_id(regid)
        )
    push.notification = jpush.notification(android=jpush.android(alert=action, extras=msg))
    print msg, push.notification
    resp = jushPushMessageToJiGuang(push)
    return resp

def jpushMessageWithTags(tags, msg, action):
    push = jpushCreateClient()
    push.audience = jpush.audience(
            jpush.tag(tags)
        )
    push.notification = jpush.notification(android=jpush.android(alert=action, extras=msg))
    resp = jushPushMessageToJiGuang(push)
    return resp


def jpushMessageWithAlias(alias, msg, action):
    push = jpushCreateClient()
    push.audience = jpush.audience(
            jpush.alias(alias)
        )
    push.notification = jpush.notification(android=jpush.android(alert=action, extras=msg))
    resp = jushPushMessageToJiGuang(push)
    return resp

def jpushMessageWithAliasTag(alias, tags, msg, action):
    push = jpushCreateClient()
    push.audience = jpush.audience(
            jpush.alias(alias),
            jpush.tag(tags)
            )
    push.notification = jpush.notification(android=jpush.android(alert=action, extras=msg))
    resp = jushPushMessageToJiGuang(push)
    return resp

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
