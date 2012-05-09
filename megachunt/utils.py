import md5

def md5hash(s):
    """
    Generates an MD5 hash from s
    """
    hash = md5.md5(s)
    return hash.hexdigest()
