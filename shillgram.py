# -*- coding: utf-8 -*-

"""shillgram

Create a sweepstakes drawing, using instagram comments as entries.
"""

import argparse
import json
import logging
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


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', '-u', help='instagram post permalink', required=True)
    parser.add_argument('--verbose', '-v', action='store_true', help='print debug logs', default=False)
    return parser.parse_args()


def make_request(url, params={}):
    if params:
        url += '?{}'.format(urllib.parse.urlencode(params))

    request = urllib.request.Request(url)

    with urllib.request.urlopen(request) as response:
        return response.status, json.loads(response.read())


def fetch_post(url):
    target = 'https://api.instagram.com/oembed'
    params = {'url': url}
    code, response = make_request(target, params=params)
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

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug('received args %s', vars(args))

    logger.info('looking up post from url %s', args.url)
    post = fetch_post(args.url)
    logger.info('found post "%s" by @%s', post['title'], post['author_name'])


if __name__ == '__main__':
    main()
