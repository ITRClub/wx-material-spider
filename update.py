#!/usr/bin/env python3
import os
import os.path
import json
import time
import random
import logging
import errno
import signal
import selenium
from functools import wraps
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

def bs(x):
    return BeautifulSoup(x, 'html.parser')

def remove_empty_files():
    for i in os.listdir():
        if os.stat(i).st_size == 0:
            logging.info('Removed empty file %s', i)
            os.remove(i)

class TimeoutError(Exception):
    pass

def timeout(func, seconds=10, error_message=os.strerror(errno.ETIME)):
    def handle_timeout(signum, frame):
        raise TimeoutError(error_message)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        signal.signal(signal.SIGALRM, handle_timeout)
        signal.alarm(seconds)
        try:
            result = func(*args, **kwargs)
        finally:
            signal.alarm(0)
        return result
    return wrapper

def mkdir_if_not_exists(x):
    if not os.path.exists(x):
        os.mkdir(x)

def valid_filename(s):
    s_2 = ''
    for c in s[:50]:
        if c in '*"/\'\\[]:;|=,<>?':
            s_2 += '_'
        else:
            s_2 += c
    return s_2
    
PA_SEARCH_HOMEPAGE='http://weixin.sogou.com/'
HOMEPAGE_SEARCH_XPATH="//div[@class='qborder2']/input[@name='query'][@id='query'][@type='text']"
HOMEPAGE_SEARCH_PA_XPATH="//div[@class='querybox']/input[@value='搜公众号']"
FIRST_PA_SEARCH_RESULT_XPATH="//a[@uigs='account_name_0']"
ARTICLE_XPATH="//div[@class='weui_msg_card_list'][@id='history']/div[@class='weui_msg_card']"
ARTICLE_CARD_XPATH=ARTICLE_XPATH+"/div[@class='weui_msg_card_bd']/div[@class='weui_media_box appmsg']/div[@class='weui_media_bd']"
ARTICLE_DATE_XPATH=ARTICLE_CARD_XPATH+"/p[@class='weui_media_extra_info']"
ARTICLE_HEADING_XPATH=ARTICLE_CARD_XPATH+"/h4[@class='weui_media_title']"
CONF_NAME='conf.json'

logging.basicConfig(level=logging.INFO)

with open(CONF_NAME) as rc:
    CONF = json.load(rc)
wd = webdriver.Chrome()

def reboot():
    global wd
    wd.quit()
    wd = webdriver.Chrome()

def check_captcha():
    if "请输入验证码" in wd.title:
        raise Exception("请输入验证码")
    
def query_for_pa_homepage(pa_name):
    input_form = wd.find_element_by_xpath(HOMEPAGE_SEARCH_XPATH)
    input_form.send_keys(pa_name)
    search_pa_button = wd.find_element_by_xpath(HOMEPAGE_SEARCH_PA_XPATH)
    search_pa_button.click()

def click_first_search_result():
    first_search_result = wd.find_element_by_xpath(FIRST_PA_SEARCH_RESULT_XPATH)
    url = first_search_result.get_attribute('href')
    reboot()
    wd.get(url)
    
def enter_article_list(pa_name):
    query_for_pa_homepage(pa_name)
    click_first_search_result()
    check_captcha()
    
def get_image(img_url):
    '''Given an images url, return a binary screenshot of it in png format.'''
    try:
        article_url = wd.current_url
        wd.get(img_url)
    except Exception as ex:
        logging.warning('failed fetching image %s', img_url)
        wd.get(article_url)

    # Get the dimensions of the browser and image.
    orig_h = wd.execute_script("return window.outerHeight")
    orig_w = wd.execute_script("return window.outerWidth")
    margin_h = orig_h - wd.execute_script("return window.innerHeight")
    margin_w = orig_w - wd.execute_script("return window.innerWidth")
    new_h = wd.execute_script('return document.getElementsByTagName("img")[0].height')
    new_w = wd.execute_script('return document.getElementsByTagName("img")[0].width')

    # Resize the browser window.
    logging.info("Getting Image: orig %sX%s, marg %sX%s, img %sX%s - %s", orig_w, orig_h, margin_w, margin_h, new_w, new_h, img_url)
    driver.set_window_size(new_w + margin_w, new_h + margin_h)

    # Get the image by taking a screenshot of the page.
    img_val = wd.get_screenshot_as_png()
    # Set the window size back to what it was.
    wd.set_window_size(orig_w, orig_h)

    # Go back to where we started.
    wd.back()
    logging.info('Success')
    return img_val

def get_image_url(img):
    url = img['src']
    if not url or url.startswith('data:'):
        url = img['data-src']
        if not url or url.startswith('data:'):
            return None
    return url
    
@timeout
def download_image_tag(no, img):
    """the second return values explains whether changes are written to disk, i.e. a image is *really* downloaded again instead of skipped"""
    url = get_image_url(img)
    if not url:
        logging.info('data encoded image, skipped')
        return None, False
    
    logging.info('Picture %d: %s', no, url)
    filename = '{}_{}.png'.format(no, valid_filename(url))

    if os.path.exists(filename):
        logging.info('Downloaded earlier')
        return filename, False
    try:
        with open(filename, 'wb') as fp:
            fp.write(get_image(url))
        return filename, True
    except Exception as ex:
        logging.info('Failure: %s', ex)
        os.remove(filename)
        return None, True
    
def download_page_images(filename):
    with open(filename) as fp: page_source = fp.read()
    soup = bs(page_source)
    img_tags = soup.find_all('img')
    if not len(img_tags): return

    pics_dir = filename + '_pics'
    mkdir_if_not_exists(pics_dir)
    os.chdir(pics_dir)
    remove_empty_files()
    changed = False # which leads to reset <filename>_imaged.html
    for no, img_tag in enumerate(img_tags):
        no += 1 # number starts from 1 instead of 0
        try:
            img_filename, is_downloaded = download_image_tag(no, img_tag)
            if not changed and is_downloaded: changed = True 
            if img_filename and img_filename != SKIPPED_TAG:
                img_tag['src'] = '{}/{}'.format(pics_dir, img_filename)
        except Exception as ex:
            logging.warning('Error while getting image %d: %s', no, ex)
    os.chdir('..')

    if changed:
        with open(filename+'_imaged.html', 'w') as fp:
            fp.write(soup.prettify())
            
def download_page(filename, article_heading):
    if os.path.exists(filename):
        logging.info('Downloaded earlier')
    else:
        article_heading.click()
        check_captcha()
        with open(filename, 'w') as fp:
            fp.write(wd.page_source)
        wd.back()

def read_article_no(no):
    for i, article_heading, article_date in enumerate(zip(wd.find_elements_by_xpath(ARTICLE_HEADING_XPATH), wd.find_elements_by_xpath(ARTICLE_DATE_XPATH))):
        if i != no: continue
        filename = valid_filename(article_date.text + ' - ' + article_heading.text)
        logging.info('Downloading article %d: %s', no, filename)
        download_page(filename, article_heading)
        download_page_images(filename)
        return

def read_articles():
    for i in range(1, 11):
        logging.info('Reading article %d', i)
        read_article_no(i)
        wd.switch_to_default_content()
    
def update_subscribes():
    mkdir_if_not_exists(CONF['mirror-dir'])
    os.chdir(CONF['mirror-dir'])
    for entry in CONF['subscribe-list']:
        reboot()
        wd.get(PA_SEARCH_HOMEPAGE)
        mkdir_if_not_exists(entry)
        os.chdir(entry)
        logging.info('PA: %s', entry)
        enter_article_list(entry)
        read_articles()
        os.chdir('..')
    os.chdir('..')

update_subscribes()

wd.quit()
