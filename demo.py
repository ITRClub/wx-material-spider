#!/usr/bin/env python3
import json
import time
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

TEST_PA_NAMES=['HFI2004', 'uncle许', '!@#$!@']
PA_SEARCH_URL='http://weixin.sogou.com/weixin?type=1&query={}'
HEADERS={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'}
ARTICLES_JSON_BEGIN_PATTERN='var msgList = '

def wget(request_url, lasttime_called=time.time()):
    while time.time()-lasttime_called < 1:
        time.sleep(1)
    lasttime_called = time.time()
    
    req = urllib.request.Request(url=request_url, headers=HEADERS)
    response = urllib.request.urlopen(req)
    bintxt = response.read()
    txt = bintxt.decode('utf-8', errors='replace')

    return txt

def bs(x):
    return BeautifulSoup(x, 'html.parser')

def get_pa_profile(pa_name):
    pa_name_encoded = urllib.parse.quote_plus(pa_name)
    request_url = PA_SEARCH_URL.format(pa_name_encoded)
    txt = wget(request_url)
    soup = bs(txt)
    divs = soup.find_all('div')

    try:
        search_results = [i for i in divs if i['class'][0] == 'txt-box']
    except KeyError:
        return 'not found'

    first_result = search_results[0]

    result_json = {
        'entry': first_result.a['href'],
        'name': first_result.a.text,
        'wechat-id': first_result.label.text
    }
    
    return result_json

def get_articles(pa_entry):
    homepage = wget(pa_entry)

    if '请输入验证码' in homepage:
        raise 'captha occured'

    msglist_start_pos = homepage.find(ARTICLES_JSON_BEGIN_PATTERN)
    msglist_end_pos = homepage.find('\n', msglist_start_pos)
    msglist_json_txt = homepage[msglist_start_pos+len(ARTICLES_JSON_BEGIN_PATTERN):msglist_end_pos-2]
    msglist_json = json.loads(msglist_json_txt)

    return msglist_json
    
for test_pa_name in TEST_PA_NAMES:
    pa_profile = get_pa_profile(test_pa_name)
    print(test_pa_name, pa_profile)

    if pa_profile == 'not found':
        continue
    
    articles = get_articles(pa_profile['entry'])
    print(json.dumps(articles, indent=2, ensure_ascii=False))
    
