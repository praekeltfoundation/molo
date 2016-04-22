from hashlib import md5


def hash(v):
    return md5(str(v)).hexdigest()
