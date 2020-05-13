from functools import wraps
from prometheus_client import Summary

from django.db import connection


database_queries = Summary(
   'database_queries', 'DB queries count'
)

request_time = Summary(
    'request_processing_seconds',
    'Time spent processing request'
)


def prometheus_query_count(func):

    @wraps(func)
    def wrap(*args, **kwargs):
        count1 = len(connection.queries)
        results = func(*args, **kwargs)
        count2 = len(connection.queries)
        count = count2 - count1
        database_queries.observe(count)
        return results

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap
