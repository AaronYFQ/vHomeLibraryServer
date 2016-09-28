#coding = utf-8
'''
the function of this file:
1. accomplish the common function
'''
def getCacheKey(cacheTag, key_prefix, version):
    return "".join([key_prefix, cacheTag, str(version)])

if __name__ == '__main__':
    print getCacheKey("xx", "YY", "01")
