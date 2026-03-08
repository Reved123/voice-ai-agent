import redis
import json

# connect to redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def save_context(session_id, data):

    r.set(session_id, json.dumps(data))


def get_context(session_id):

    context = r.get(session_id)

    if context:
        return json.loads(context)

    return {}