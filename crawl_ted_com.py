# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import sys
import os

modules_3rd = os.path.dirname(__file__)
modules_3rd = os.path.join(modules_3rd, '3rd')
sys.path.append(modules_3rd)

import logging
from argparse import ArgumentParser
from cted import crawl_ted

def read_url_list(path):
    """TODO: Docstring for read_url_list.

    :path: TODO
    :returns: TODO

    """
    with open(path) as f:
        return [s.strip() for s in f if s.strip()]

def get_conf():
    """TODO: Docstring for get_conf.
    :returns: TODO

    """
    parser = ArgumentParser(description='Download subtitles of TED talks')
    parser.add_argument('--langs', nargs='+', required=True, help='Languages to download')
    parser.add_argument('--output', required=True, help='Directory for saving text')
    parser.add_argument('--ignore', default=(), type=read_url_list, help='Url to ignore')
    return parser.parse_args()

def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    conf = get_conf()
    crawl_ted(conf.langs, conf.output, conf.ignore)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
