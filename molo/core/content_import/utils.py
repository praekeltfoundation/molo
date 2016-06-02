from hashlib import md5


def hash(v):
    return md5(str(v)).hexdigest()


def conj(a, b):
    res = {}
    res.update(a)
    res.update(b)
    return res


def omit_nones(d):
    return dict((k, v) for k, v in d.iteritems() if v is not None)


def schedule(task, delay=True, *a, **kw):
    if delay:
        return task.delay(*a, **kw)
    else:
        return task(*a, **kw)
