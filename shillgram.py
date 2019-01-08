# -*- coding: utf-8 -*-

"""shillgram

Create a sweepstakes drawing, using instagram comments as entries.
"""

import argparse
import logging
import urllib


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
        return response.status, response.read()


def main():
    args = get_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug('received args %s', vars(args))


if __name__ == '__main__':
    main()
