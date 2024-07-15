async def set_redis_value(redis, key, value):
    await redis.set(key, value)


async def get_redis_value(redis, key):
    return await redis.get(key)


async def find_key_by_value(redis, search_value):
    async for key in redis.scan_iter():
        value = await redis.get(key)
        if value == search_value:
            return key
    return None
