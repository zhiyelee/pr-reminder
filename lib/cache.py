
import redis
from helpers.config import (REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)

class RedisCache(object):
    def __init__(self):
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_PASSWORD)
    
    def set(self, key, value):
        return self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)

cache = RedisCache()
    
