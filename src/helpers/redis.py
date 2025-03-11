# Redis helper
#
# Functions to help read and write from Redis


import json

import redis

from config import config


class RedisConnect:
    def __init__(self):
        # Load global variables
        self.r = redis.Redis(  # Connect to Redis
            host=config.redis.url, port=config.redis.port, decode_responses=True
        )

    def redis_read(self, key):  # Read data from Redis
        results = self.r.get(key)  # Get the latest results from Redis for a given key

        if results:
            data = json.loads(results)
        else:
            data = ""

        return data

    def redis_write(self, key, data, ttl):  # Write data to Redis
        write = self.r.set(key, json.dumps(data), ttl)  # Store data with a given TTL

        return write
