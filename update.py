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
SKIPPED_TAG='//skipped//'
CONF_NAME='conf.json'

with open(CONF_NAME) as rc:
    CONF=json.load(rc)

logging.basicConfig(level=logging.INFO)
wd = webdriver.Chrome()

def wait(lasttime_called=time.time()):
    while time.time()-lasttime_called < CONF['wait']:
        time.sleep(CONF['wait'])
    lasttime_called = time.time()

def random_wait(t):
    time.sleep((1+random.random()) * t)

def ctrl_x(x): # ctrl+x
    ActionChains(wd).key_down(Keys.CONTROL).send_keys(x).key_up(Keys.CONTROL).perform()
    
def change_to_tab(no): # ctrl+1 ctrl+2 etc.
    ctrl_x(no)
    
def close_tab(): # ctrl+w
    ctrl_x('w')

def reboot():
    global wd
    wd.quit()
    wd = webdriver.Chrome()
    
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

def get_image(img_url, driver=wd):
    '''Given an images url, return a binary screenshot of it in png format.'''
    driver.get(img_url)

    # Get the dimensions of the browser and image.
    orig_h = driver.execute_script("return window.outerHeight")
    orig_w = driver.execute_script("return window.outerWidth")
    margin_h = orig_h - driver.execute_script("return window.innerHeight")
    margin_w = orig_w - driver.execute_script("return window.innerWidth")
    new_h = driver.execute_script('return document.getElementsByTagName("img")[0].height')
    new_w = driver.execute_script('return document.getElementsByTagName("img")[0].width')

    # Resize the browser window.
    logging.info("Getting Image: orig %sX%s, marg %sX%s, img %sX%s - %s", orig_w, orig_h, margin_w, margin_h, new_w, new_h, img_url)
    driver.set_window_size(new_w + margin_w, new_h + margin_h)

    # Get the image by taking a screenshot of the page.
    img_val = driver.get_screenshot_as_png()
    # Set the window size back to what it was.
    driver.set_window_size(orig_w, orig_h)

    # Go back to where we started.
    driver.back()
    logging.info('Success')
    return img_val

def test_get_image():
    with open('test_get_image.png', 'wb') as fp:
        fp.write(get_image('http://img04.sogoucdn.com/v2/thumb/resize/w/520/h/300/ir/3/zi/on/iw/130/ih/75/crop/x/0/y/0/w/520/h/300/xy/center?t=2&appid=200524&url=https%3A%2F%2Fichef.bbci.co.uk%2Fnews%2F624%2Fcpsprodpb%2F1722A%2Fproduction%2F_100326749_045400167-1.jpg'))

@timeout
def download_page_image_no(no, retry=10):
    imgs = wd.find_elements_by_tag_name('img')
    for count,img in enumerate(imgs):
        if count+1 != no:
            continue

        while True:
            try:
                url = img.get_attribute('src')
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                if not retry: raise
                logging('Picture %d: retrying(%d) after 2 sec', no, retry)
                time.sleep(2)
                retry -= 1
        if not url or url.startswith('data:'):
            url = img.get_attribute('data-src')
            if not url or url.startswith('data:'):
                logging.info('Skipped')
                return SKIPPED_TAG
        logging.info('Picture %d: %s', no, url)
        filename = '{}_{}.png'.format(no, valid_filename(url))
        try:
            with open(filename, 'wb') as fp:
                fp.write(get_image(url))
        except Exception as ex:
            logging.info('Failure: %s', ex)
            os.remove(filename)
        return filename
    
def download_page_images(filename):
    imgs = wd.find_elements_by_tag_name('img')
    if not len(imgs):
        return
    img_replaced_soup = bs(wd.page_source)
    img_filenames = [None for i in range(len(imgs))]
    
    pics_dir = filename + '_pics'
    mkdir_if_not_exists(pics_dir)
    os.chdir(pics_dir)
    for no in range(1, len(imgs)+1):
        try:
            while True:
                img_filename = download_page_image_no(no)
                if img_filename:
                    img_filenames[no-1] = img_filename
                    break
        except TimeoutError:
            logging.warning('Timeout while getting image %d', no)
        except Exception as ex:
            logging.warning('Error while getting image %d: %s', no, ex)
            wd.back()
    os.chdir('..')

    logging.info(img_filenames)
    for no,img_tag in enumerate(img_replaced_soup.find_all('img')):
        if no >= len(img_filenames): break
        img_filename = img_filenames[no]
        if img_filename and img_filename != SKIPPED_TAG:
            logging.info('Replacing <img> %d', no)
            img_tag['src'] = '{}/{}'.format(pics_dir, img_filename)
    with open(filename+'_imaged.html', 'w') as fp:
        fp.write(img_replaced_soup.prettify())
            
def download_page(filename):
    with open(filename, 'w') as fp:
        fp.write(wd.page_source)

def test_download_page():
    wd.get("http://sports.sina.com.cn/china/afccl/2018-03-08/doc-ifxpwyhw0399024.shtml")
    download_page()

def test_download_page_images():
    wd.get('https://mp.weixin.qq.com/s?timestamp=1520730796&src=3&ver=1&signature=b900V7P4dwKxlBxvfnwqeMz0cfAJTXx6S4j-mrCoJ1KXipXpZ8RjVVPJg0lpBFVdx6fKInKoKUV9o*bXA0DXuYy1MY6BaN8Ah4ipgjW*bgQttHYh0Z2j2HQpQ4*jCmXPl6IGiMJCInaGx78KWmqaaV-mOrjwfPyLAD4pdzg6emg=') 
    #wd.get("http://sports.sina.com.cn/china/afccl/2018-03-08/doc-ifxpwyhw0399024.shtml")
    download_page_images('test_download_page_images')
    
def read_article_no(no):
    count = no
    for article_heading, article_date in zip(wd.find_elements_by_xpath(ARTICLE_HEADING_XPATH), wd.find_elements_by_xpath(ARTICLE_DATE_XPATH)):
        if count > 1:
            count -= 1
            logging.info('Not this one. Next.')
            continue
        filename = valid_filename(article_date.text + ' - ' + article_heading.text)
        logging.info(filename)
        if os.path.exists(filename):
            logging.info('Downloaded earlier')
            return
        else:
            logging.info('Article[%d] %s', no, filename)
            article_heading.click()
            download_page(filename)
            download_page_images(filename)
            wd.back()
            return

def read_articles():
    for i in range(1, 11):
        logging.info('Reading article %d', i)
        read_article_no(i)
        
def test_read_articles():
    mkdir_if_not_exists('HFI2004')
    os.chdir('HFI2004')
    wd.get('https://mp.weixin.qq.com/profile?src=3&timestamp=1520737557&ver=1&signature=apzTz2OJCykfArpu8*CXWXtK-vn8ihw-sfnYpqhs0SXWG3F6yDN6X2hJ2IasdxjX9BaLCrxKHZJwXD*Ixv2MOA==')
    read_articles()
    os.chdir('..')
    
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

os.chdir('test')
#test_read_articles()
#test_download_page()
#test_download_page_images()
#test_get_image()
os.chdir('..')

wd.quit()
