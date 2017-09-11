# -*- coding: utf-8 -*-

import argparse
import os
import requests
import selenium
import time 
import urllib
import urllib.parse as urlparse 

from functools import partial

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def search_google_image(image_url):

    def load_more_image(element):
        for _ in range(20):
            element.send_keys(Keys.END)
            time.sleep(0.2)

    search_url = f'https://images.google.com/searchbyimage?image_url={image_url}&encoded_image=&image_content=&filename=&hl=ko'
    
    browser = webdriver.Chrome()

    browser.get(search_url)
    time.sleep(1)

    browser.find_element_by_class_name('iu-card-header').click()
    time.sleep(1)

    element = browser.find_element_by_tag_name('body')

    load_more_image(element)
    try:
        browser.find_element_by_class_name('_kvc').click()
        load_more_image(element)
    except:
        pass

    html_source = browser.page_source
    browser.close()

    return html_source 


def get_image_urls(page_source):
    bs_page_source = BeautifulSoup(str(page_source), "html.parser")
    image_container = bs_page_source.find('div', {'id': 'rg'})

    image_urls = []
    for link in image_container.find_all('a'):
        try:
            link = urlparse.urlparse(link.attrs['href'])
            link_qs = urlparse.parse_qs(link.query)
            image_url = link_qs['imgurl'][0]
            image_urls.append(image_url)
        except:
            pass

    return image_urls
    

def download_image(save_path, link):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    try:
        r = requests.get(link[-1])
        assert(r.status_code == 200)
    except:
        print(f'Cannot get link {link}')
        return None
    
    urllib.request.urlretrieve(link[-1], os.path.join(save_path, f'{link[0]}-{link[1]}.jpeg'))

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('savepath', help='absolute save path')
    parser.add_argument(
            '--worker',
            help='the numter of worker used for downloading images',
            type=int,
            default=4
    )


    args = parser.parse_args()

    image_url = input("Type image url: ")
    image_save_prefix = input("Type image save prefix: ")

    html_source = search_google_image(image_url)
    image_urls = get_image_urls(html_source)
    enum_image_urls = [(image_save_prefix, str(i), image_url) for i, image_url in enumerate(image_urls)]
    
    print(f"Found Image Count: {len(enum_image_urls)}")
    
    from multiprocessing import Pool
    
    with Pool(processes=args.worker) as p:
        func = partial(download_image, args.savepath)
        p.map(func, enum_image_urls)

