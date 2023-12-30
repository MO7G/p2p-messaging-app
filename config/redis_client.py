# redis_client.py
import redis

# Create a global Redis client instance
redis_client = redis.Redis(
    host='redis-15092.c274.us-east-1-3.ec2.cloud.redislabs.com',
    port=15092,
    password='kyzprwjfImZdMc32sye3PyRTQwi2VdfY')
