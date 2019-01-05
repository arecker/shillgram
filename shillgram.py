import subprocess

import InstagramAPI
import requests


def make_client(user='alex_recker'):
    password = subprocess.run(
        ['pass', 'instagram'], stdout=subprocess.PIPE
    ).stdout.decode()
    client = InstagramAPI.InstagramAPI(user, password)
    client.login()
    return client


def get_media_id(post_url):
    return requests.get('http://api.instagram.com/oembed', params={
        'url': post_url
    }).json()['media_id']


def count_comments(post_url):
    client = make_client()
    media_id = get_media_id(post_url)
    max_id = ''
    count = 0

    while True:
        client.getMediaComments(media_id, max_id=max_id)
        count += len(client.LastJson['comments'])

        if not client.LastJson.get('has_more_comments', False):
            break

        max_id = client.LastJson['next_max_id']

    return count
