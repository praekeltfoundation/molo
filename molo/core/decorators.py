from functools import wraps
from django.db import connection
from prometheus_client import Summary


DATABASE_QUERIES = Summary(
   'database_queries', 'DB queries count'
)


def prometheus_query_count(func):

    @wraps(func)
    def wrap(*args, **kwargs):
        count1 = len(connection.queries)
        results = func(*args, **kwargs)
        count2 = len(connection.queries)
        count = count2 - count1
        DATABASE_QUERIES.observe(count)
        return results

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap
