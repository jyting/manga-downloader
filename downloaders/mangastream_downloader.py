import requests
from urllib import request
from pyquery import PyQuery as pq
import pdb
import os

import ctypes

from downloaders import download_base

def glibc_fix():
    libc = ctypes.cdll.LoadLibrary('libc.so.6')
    res_init = libc.__res_init
    res_init()

class MangaStreamDownloader(download_base.MangaDownloader):
    def __init__(self):
        super().__init__(url='http://www.mangastream.com')

    def get_img_url_from_html(self, url):
        """
        Extracts image url from page containing image
        """
        html = request.urlopen(url).read().decode('utf-8')
        q = pq(html)
        img_url = q("#manga-page").attr('src')
        return img_url
    
    def get_page_paths_from_html(self, html):
        """
        Extracts list of page paths from any given page of the chapter. Assumes
        that every page of chapters will contain the dropdown menu to select page
        """
        q = pq(html)
        dropdown_options = q('.btn-reader-page').children('ul').children('li')
        page_paths = [pq(d).children('a').attr('href') for d in dropdown_options]
        return page_paths
    
    def get_chapter_url(self, manga, chapter):
        url = 'http://mangastream.com/manga/{}'.format(manga)
        html = request.urlopen(url).read().decode('utf-8')
        q = pq(html)
        chapter_table_items = q('.table-striped').find('a')
        # chapter_urls = [pq(item).attr('href') for item in chapter_table_items]
        chapter_urls = [pq(item).attr('href') for item in chapter_table_items if str(chapter) in pq(item).attr('href')]
        try:
            return chapter_urls[0]
        except IndexError:
            print('Chapter: {} for manga: {} not found on Mangastream.')
    
    def download_chapter(self, manga, chapter):
        """
        Downloads specific chapter of manga
        """
        glibc_fix()
        # first_url = '{}/{}/{}'.format(self.base_url, manga, chapter)
        first_url = self.get_chapter_url(manga, chapter)
        html = request.urlopen(first_url).read().decode('utf-8')
        page_paths = self.get_page_paths_from_html(html)
        chapter_str = str(chapter)
        os.makedirs('{}'.format(chapter_str))
        for num, page_path in enumerate(page_paths):
            page_url = page_path
            self.download_img_from_url(page_url, '{}/{}.jpg'.format(chapter_str, self.pad_number(num)))
