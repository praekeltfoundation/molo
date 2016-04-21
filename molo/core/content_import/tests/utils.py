def catch(error_cls, fn):
    try:
        fn()
        return None
    except error_cls as e:
        return e
