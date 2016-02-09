# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
import re
import time
import os
from codecs import open as copen
from unicodedata import category
from itertools import count
from requests import get
from bs4 import BeautifulSoup
from boltons.iterutils import windowed_iter
from boltons.cacheutils import cached

crawler_cache = {}
log = logging.getLogger(__name__)

pages_tmpl = 'http://www.ted.com/talks?page={}'
time_re = re.compile(r'^\d{1,2}:\d{1,2}(.*)')
dot_re = re.compile(r'.*[.!?]$')

class ConnectionError(Exception):
    pass

class UrlError(Exception):
    pass

class ParseError(Exception):
    pass

@cached(crawler_cache)
def get_html(url):
    """TODO: Docstring for get_html.

    :url: TODO
    :returns: TODO

    """
    try:
        result = get(url)
    except:
        raise ConnectionError(url)
    if result.status_code // 100 != 2:
        raise UrlError(url)
    return result.text

def get_html_retry(url):
    """TODO: Docstring for get_html_retry.

    :url: TODO
    :returns: TODO

    """
    while True:
        try:
            return get_html(url)
        except ConnectionError:
            log.warn('Connection error, retrying in 30 seconds')
            time.sleep(30)
        except UrlError:
            return None

def get_processed(html, processor):
    """TODO: Docstring for get_processed.

    :html: TODO
    :processor: TODO
    :returns: TODO

    """
    bs = BeautifulSoup(html)
    result = processor(bs)
    if not result:
        raise ParseError()
    return result

def get_pages():
    """TODO: Docstring for get_pages.
    :returns: TODO

    """
    for i in count(start=1):
        yield pages_tmpl.format(i)

def get_talks(bs):
    """TODO: Docstring for get_talks.

    :bs: TODO
    :returns: TODO

    """
    urls = []
    for div in bs.find_all('div', class_='talk-link'):
        link = div.find('div', class_='media__message').find('a')
        if link['href'].startswith('/talks/'):
            urls.append('http://www.ted.com' + link['href'])
    return urls

def get_transcript(bs):
    """TODO: Docstring for get_transcript.
    :returns: TODO

    """
    lines = []
    for p in bs.find_all('p', class_='talk-transcript__para'):
        text = ' '.join(p.stripped_strings)
        text = ' '.join(text.split())
        if time_re.match(text):
            cleaned = time_re.match(text).group(1).strip()
            if cleaned:
                text = cleaned
        lines.append(text)
    lines = ' '.join(lines).split()
    sents = []
    sent = []
    for s1, s2 in windowed_iter(lines, 2):
        sent.append(s1)
        if dot_re.match(s1) and s2 and category(s2[0]) == 'Lu':
            sents.append(' '.join(sent))
            sent = []
    return sents

def crawl_ted(langs, output, ignore_urls=()):
    crawl_id = str(int(time.time()))
    ignore = [u.split('/')[-1] for u in ignore_urls]
    for lang in langs:
        log.info('Language %s', lang)
        path = os.path.join(output, crawl_id + '_' + lang)
        log.info('Saving into file %s', path)
        with copen(path, 'w', encoding='utf-8') as f:
            for url in get_pages():
                log.info('Page %s', url)
                html = get_html_retry(url)
                if html is None:
                    break
                try:
                    for talk_url in get_processed(html, get_talks):
                        if talk_url.split('/')[-1] in ignore:
                            log.info('Ignoring %s', talk_url)
                            continue
                        talk_url += '/transcript?language=' + lang
                        log.info('Talk %s', talk_url)
                        talk_html = get_html_retry(talk_url)
                        if talk_html is None:
                            continue
                        try:
                            lines = get_processed(talk_html, get_transcript)
                        except ParseError:
                            pass
                        else:
                            f.write('\n'.join(lines))
                except ParseError:
                    break
    log.info('Done')
