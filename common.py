from collections import Counter
from mongo_db import db
import uuid


async def create_short_url(long_url, short_url=None, user_id=None):
    if short_url:
        exists_short_url = await db.links.find_one({'short_url': short_url})
        if exists_short_url:
            return {'error': 'short link already created'}
    else:
        short_url = str(uuid.uuid4())
    data = {'short_url': short_url, 'long_url': long_url}
    if data:
        data['user_id'] = user_id
    await db.links.insert_one(data)
    return short_url


async def short_url_to_long(short_url: str):
    original_link = await db.links.find_one({'short_url': short_url})
    if not original_link:
        return "Not in base"
    return original_link['long_url']


async def get_all_urls(user_id):
    links = db.links.find({'user_id': user_id})
    return links


async def redirect_count(user_id):
    result = []
    data = db.redirects.find({'owner': user_id})
    async for val in data:
        result.append(val['short_url'])
    redirect_counts = Counter(result)
    return redirect_counts
