#!/usr/bin/env python3
import os
import os.path
import json
import time
import random
import logging
from selenium import webdriver

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

def query_for_pa_homepage(pa_name):
    input_form = wd.find_element_by_xpath(HOMEPAGE_SEARCH_XPATH)
    input_form.send_keys(pa_name)
    search_pa_button = wd.find_element_by_xpath(HOMEPAGE_SEARCH_PA_XPATH)
    search_pa_button.click()

def click_first_search_result():
    first_search_result = wd.find_element_by_xpath(FIRST_PA_SEARCH_RESULT_XPATH)
    first_search_result.click()
    
def enter_article_list(pa_name):
    query_for_pa_homepage(pa_name)
    click_first_search_result()
    
def read_article_no(no):
    count = no
    for article_heading, article_date in zip(wd.find_elements_by_xpath(ARTICLE_HEADING_XPATH), wd.find_elements_by_xpath(ARTICLE_DATE_XPATH)):
        if count > 1:
            count -= 1
            continue

        filename = valid_filename(article_date.text + ' - ' + article_heading.text)
        logging.info('Article[%d] %s', no, filename)
        if not os.path.exists(filename):
            article_heading.click()
            with open(filename+'.html', 'w') as fp:
                fp.write(wd.page_source)

            imgs = []
            for i in wd.find_elements_by_tag_name('img'):
                url = i.get_attribute('data-src')
                if url:
                    imgs += url
            if len(imgs):
                pics_dir = filename + '_pics'
                os.mkdir(pics_dir)
                os.chdir(pics_dir)
                no = 1
                for img in imgs:
                    logging.info('Picture %d: %s', no, img)
                    try:
                        wd.get(img)
                    except selenium.common.exceptions.WebDriverException:
                        logging.info('Download failed')
                        continue
                    wd.save_screenshot('{}_{}.png'.format(no, valid_filename(img)))
                    no += 1
                    wd.back()
                os.chdir('..')
                
            wd.back()
        return

def read_articles():
    for i in range(1, 11):
        read_article_no(i)
        
def test_read_articles():
    os.chdir('HFI2004')
    wd.get('http://mp.weixin.qq.com/profile?src=3&timestamp=1520685495&ver=1&signature=apzTz2OJCykfArpu8*CXWXtK-vn8ihw-sfnYpqhs0SXWG3F6yDN6X2hJ2IasdxjXwTFy3Ex-iZj*BIyrCs81oA==')
    read_articles()
    os.chdir('..')
    
def update_subscribes():
    wd.get(PA_SEARCH_HOMEPAGE)
    for entry in CONF['subscribe-list']:
        mkdir_if_not_exists(entry)
        os.chdir(entry)
        enter_article_list(entry)
        read_articles()
        wd.back()
        os.chdir('..')

mkdir_if_not_exists(CONF['mirror-dir'])
os.chdir(CONF['mirror-dir'])

#update_subscribes()
test_read_articles()

wd.quit()
