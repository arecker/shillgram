import collections
import random
import subprocess

import InstagramAPI
import requests


class CommentIterator(object):
    def __init__(self, client=None, media_id=''):
        self.client = client
        self.media_id = media_id
        self.has_more_comments = False

    def __len__(self):
        self.client.getMediaComments(self.media_id)
        return self.client.LastJson['comment_count']

    def __iter__(self):
        max_id = ''

        while True:
            self.client.getMediaComments(self.media_id, max_id=max_id)
            yield from reversed(self.client.LastJson['comments'])

            if not self.client.LastJson.get('has_more_comments', False):
                break

            max_id = self.client.LastJson['next_max_id']


class Post(object):

    def __init__(self, client=None, url=''):
        self.client = client
        self.url = url

        response = requests.get('http://api.instagram.com/oembed', params={
            'url': self.url
        }).json()

        self.media_id = response['media_id']

        self.comments = CommentIterator(client=client, media_id=self.media_id)


def make_client(user='alex_recker'):
    password = subprocess.run(
        ['pass', 'instagram'], stdout=subprocess.PIPE
    ).stdout.decode()
    client = InstagramAPI.InstagramAPI(user, password)
    client.login()
    return client


def tags_from_text(text):
    return list(filter(None, [
        word[1:]
        for word
        in text.split(' ')
        if word.startswith('@')
    ]))


def contest(url, max_entries=10):

    """contest

    pick a random winner from comments, where each tagged friend is
    one chance to win
    """

    participants = collections.defaultdict(list)

    for comment in Post(client=make_client(), url=url).comments:
        user = comment['user']['username']
        friends = tags_from_text(comment['text'])

        while friends and len(participants[user]) < max_entries:
            friend = friends.pop(0)
            if friend != user and friend not in participants[user]:
                participants[user].append(friend)

    weighted = []

    for user, friends in participants.items():
        weighted += [user for i in range(len(friends))]

    return random.choice(weighted)
