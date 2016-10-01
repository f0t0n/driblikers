import aiohttp
import asyncio
import itertools
import operator
import sys
from collections import defaultdict
from functools import partial


def get_config():
    return {
        'access_token':
            'b0111b18d68127c837284a17928a8660dc9e0b7f8ee3a1544bcfea3541abc50e',
        'api_url': 'https://api.dribbble.com/v1',
    }


def get_auth(access_token):
    return {
        'Authorization': 'Bearer {}'.format(access_token)
    }


def join_url_parts(*parts):
    return '/'.join(parts)


def create_client(loop):
    return aiohttp.ClientSession(loop=loop)


def get_resource_url(api_url, resource_name):
    return join_url_parts(api_url, resource_name)


async def fetch_from_url(client, access_token, url, success=200):
    async with client.get(url, headers=get_auth(access_token)) as resp:
        assert resp.status == success
        return await resp.json()


def create_loop():
    return asyncio.get_event_loop()


async def get_shot_likes(shot, fetch):
    return await fetch(shot['likes_url'])


async def get_top_likers(shots, fetch, top=10):
    results = await asyncio.gather(*[get_shot_likes(shot, fetch)
                                     for shot in shots])
    likes = list(itertools.chain(*results))
    likers = [like['user'] for like in likes]
    likers_by_id = {user['id']: user for user in likers}
    likers_dict = defaultdict(int)
    for liker in likers:
        likers_dict[liker['id']] += 1
    sorted_likers = sorted(likers_dict.items(), key=operator.itemgetter(1),
                           reverse=True)
    return [(likers_by_id[x[0]], x[1]) for x in sorted_likers[:top]]


def liker_str(liker):
    user = liker[0]
    likes_cnt = liker[1]
    return '{} ({}): {} like(s)'.format(user['username'], user['name'],
                                        likes_cnt)


def print_liker(i, liker):
    print('{}.\t{}'.format(i, liker_str(liker)))


def get_username():
    try:
        return sys.argv[1]
    except IndexError:
        return 'justinpervorse'  # some default user


async def run(loop):
    username = get_username()
    config = get_config()
    client = create_client(loop)
    url_for = partial(get_resource_url, config['api_url'])
    fetch = partial(fetch_from_url, client, config['access_token'])
    user = await fetch(join_url_parts(url_for('users'), username))
    shots = await fetch(user['shots_url'])
    likers = await get_top_likers(shots, fetch)
    print('Top 10 likers of {}:'.format(username))
    for i, liker in enumerate(likers, start=1):
        print_liker(i, liker)
    await client.close()


if __name__ == '__main__':
    loop = create_loop()
    loop.run_until_complete(run(loop))
    loop.close()

