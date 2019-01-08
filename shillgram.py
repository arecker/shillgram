# -*- coding: utf-8 -*-

"""Create a sweepstakes drawing, using instagram comments as entries."""

import argparse
import json
import logging
import sys
import urllib.parse
import urllib.request


def make_logger():
    logger = logging.getLogger('shillgram')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = make_logger()


class FourOhFour(Exception):
    pass


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', '-u', help='instagram post permalink', required=True)
    parser.add_argument('--verbose', '-v', action='store_true', help='print debug logs', default=False)
    parser.add_argument('--quiet', '-q', action='store_true', help='hide all output except winner', default=False)
    return parser.parse_args()


def make_request(url, params={}):
    if params:
        url += '?{}'.format(urllib.parse.urlencode(params))

    request = urllib.request.Request(url)

    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise FourOhFour


def fetch_post(url):
    target = 'https://api.instagram.com/oembed'
    params = {'url': url}
    _, response = make_request(target, params=params)
    keys = ('media_id', 'title', 'author_name')
    return dict([(key, val) for key, val in response.items() if key in keys])


def yada_yada(text, max_chars=30, ending='...'):
    words = text.split(' ')
    shortened_text = ''

    while len(shortened_text) <= max_chars - len(ending):
        try:
            word = words.pop(0)
            if shortened_text:
                word = ' ' + word
            shortened_text += word
        except IndexError:
            break

    return '{}{}'.format(shortened_text, ending)


def main():
    args = get_args()

    if args.quiet:
        logger.handlers = []
    elif args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug('received args %s', vars(args))

    logger.info('looking up post from url %s', args.url)
    try:
        post = fetch_post(args.url)
    except FourOhFour:
        logger.error('cannot find post for url %s', args.url)
        sys.exit(1)

    logger.info('found post "%s" by @%s', yada_yada(post['title']), post['author_name'])


if __name__ == '__main__':
    main()
