#coding = utf-8

def getCacheKey(cacheTag, key_prefix, version):
    return "".join([key_prefix, cacheTag, str(version)])

if __name__ == '__main__':
    print getCacheKey("xx", "YY", "01")
