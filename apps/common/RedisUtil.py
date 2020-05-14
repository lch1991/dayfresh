from django_redis import get_redis_connection


class RedisUtil(object):
    def __init__(self):
        conn = get_redis_connection('default')
        self.connection = conn

    def set(self, key, value, time):
        if time is not None:
            self.connection.set(key, value, time)
        else:
            self.connection.set(key, value)

    def get(self, key):
        value = self.connection.get(key)
        return value

    def delete(self, key):
        self.connection.delete(key)