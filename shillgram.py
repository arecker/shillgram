import collections
import contextlib
import os
import random
import sys

import click
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

    @property
    def author(self):
        try:
            return self._author
        except AttributeError:
            self.client.getMediaComments(self.media_id)
            self._author = self.client.LastJson['caption']['user']['username']
            return self._author


@contextlib.contextmanager
def hidden_output():
    _stderr, _stdout = sys.stderr, sys.stdout
    with open(os.devnull, 'w') as nothing:
        try:
            sys.stdout = sys.stderr = nothing
            yield
        finally:
            sys.stderr = _stderr
            sys.stdout = _stdout


def make_client(username, password):
    client = InstagramAPI.InstagramAPI(username, password)
    with hidden_output():
        client.login()
    return client


def tags_from_text(text):
    return list(filter(None, [
        word[1:]
        for word
        in text.split(' ')
        if word.startswith('@')
    ]))


@click.group()
def cli():

    """shillgram - helping instagram shills shill even harder"""


@cli.command()
@click.option('--url', prompt=True)
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--max-entries', default=10)
@click.option('--no-tagging', is_flag=True, default=False)
def contest(url, username, password, max_entries, no_tagging):

    """pick a random winner from comments"""

    participants = collections.defaultdict(list)

    click.echo('authenticating with instagram')
    client = make_client(username, password)

    click.echo('fetching post')
    post = Post(client=client, url=url)

    click.echo('analyzing comments')
    with click.progressbar(post.comments) as comments:
        for comment in comments:
            user = comment['user']['username']

            if no_tagging:
                # just add a single dummy friend since each comment
                # just counts as one entry
                participants[user] = [user]
                continue

            friends = tags_from_text(comment['text'])
            while friends and len(participants[user]) < max_entries:
                friend = friends.pop(0)

                is_author = friend == post.author
                is_tagged = friend in participants[user]
                is_user = friend == user

                if not any([is_author, is_tagged, is_user]):
                    participants[user].append(friend)

    click.echo('building weighted list')
    weighted = []
    for user, friends in participants.items():
        weighted += [user for i in range(len(friends))]

    if not weighted:
        click.echo('oops - nobody tagged nobody for nothing!')
        exit(1)

    click.echo('selecting a winner')
    winner = random.choice(weighted)

    click.echo('The winner is @{}'.format(winner))

    if not no_tagging:
        click.echo('Tagged friends: {}'.format(', '.join([
            '@{}'.format(friend)
            for friend
            in participants[winner]
        ])))


if __name__ == '__main__':
    cli()
