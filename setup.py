from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='shillgram',
    version='0.1',
    py_modules=['shillgram'],
    install_requires=[
        'Click==7.0',
        'InstagramAPI==1.0.2',
        'requests==2.11.1'
    ],
    entry_points='''
        [console_scripts]
        shillgram=shillgram:cli
    ''',
)
