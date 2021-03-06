# coding: utf-8
# Author：fengchi863
# WeChat：lucien863
# Date ：2020/6/17 15:43

'''
下载东方财富的个股研报，使用该文件请参照我的github里的目录结构进行复制，
能直接克隆整个工程就更好了
'''

import json
import logging
import os
import random
import re
import socket
import time
import urllib
from urllib import request

from bs4 import BeautifulSoup

from stock_info import get_index_cons_list

# 全局变量
MIN_PAPER_SIZE = 6  # 不能低于MIN_PAPER_SIZE页

timeout = 20
socket.setdefaulttimeout(timeout)  # 这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置
sleep_download_time = 10
time.sleep(sleep_download_time)  # 这里时间自己设定

# 一般化配置logging
logger = logging.getLogger()
logger.setLevel('DEBUG')
now_datetime = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
log_file_path = 'log/'
log_file_name = 'fetch_report_%s.log' % now_datetime

formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d - %(levelname)s: %(message)s')
fh = logging.FileHandler(log_file_path + log_file_name, mode='w')
fh.setLevel(logging.DEBUG)
sh = logging.StreamHandler()  # 往Python Console控制台输出
sh.setFormatter(formatter)
fh.setFormatter(formatter)  # 往文件输出
logger.addHandler(sh)
logger.addHandler(fh)


def remove_special_chars(title: str):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "", title)
    return new_title


# def read_file(filename):
#     f = open(filename, 'r')
#     return f.read()
#
#
# stock_list = read_file('StockToAdd.txt').split(',')
stock_list = get_index_cons_list('000300')


# 请求头
def get_user_agent():
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36',
        'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0) Gecko/20100101 Firefox/17.0.6',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
        'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    ]
    user_agent = {'User-Agent': random.choice(user_agent_list)}
    return user_agent


def download_paper(use_proxy=True):
    for stk_id in stock_list:
        try:
            logger.info(stk_id + '开始下载...')

            # 检测是否有该股票的目录
            exists_stk_list = list(map(lambda x: x.split('_')[1], os.listdir('report/')))
            if stk_id in exists_stk_list:
                logger.info(stk_id + '已存在')
                continue

            for page_no in range(1, 10):
                url = "http://reportapi.eastmoney.com/report/list?cb=&pageNo={}&pageSize=80&" \
                      "code={}&industryCode=*&industry=*&rating=*&ratingchange=*&" \
                      "beginTime=2016-1-1&endTime=2020-6-17&fields=&qType=0&_="
                url = url.format(page_no, stk_id)

                user_agent = get_user_agent()

                if use_proxy:
                    # 设置代理
                    print('使用代理！')
                    proxy = '183.207.194.202:3128'  # 使用代理
                    proxy_values = "%(ip)s" % {'ip': proxy}
                    proxies = {
                        'http': 'http://' + proxy_values,
                        'https': 'https://' + proxy_values
                    }
                    handler = urllib.request.ProxyHandler(proxies)
                    opener = urllib.request.build_opener(handler)

                    req = request.Request(url, headers=user_agent)
                    try:
                        sout = opener.open(req, timeout=200)
                    except urllib.request.URLError as e:
                        if isinstance(e.reason, socket.timeout):
                            logger.error('socket timed out - URL %s', url)
                        else:
                            logger.error(e.reason)
                        print('连接异常')
                    except request.HTTPError as e:
                        logging.info('HTTPError code: ' + str(e.code))
                    except socket.timeout:
                        logger.error('socket timed out - URL %s', url)
                    sout = sout.read().decode("utf8")
                    print('代理加载成功')
                else:
                    print('不使用代理...')
                    req = request.Request(url, headers=user_agent)
                    sout = request.urlopen(req, timeout=200)
                    sout = sout.read().decode("utf8")

                for i in range(len(sout)):
                    if sout[i:i + 4] == 'data':
                        sout = sout[i:-1]
                sout = '{"' + sout + '}'  # 增加json头和尾方便解析

                decode_json = json.loads(sout)
                report_data_list = decode_json["data"]
                download_list = []
                for j in range(0, len(report_data_list)):
                    '''
                    attachPages: 报告页数，可以根据这个变量筛选深度报告(>10)
                    encodeUrl: 要下载的pdf尾缀
                    orgSName: 机构名称
                    '''
                    # if report_data_list[j]['publishDate'][:10] > '2017-01-26':
                    #     continue
                    # 剔除10页以下的研报
                    if report_data_list[j]['attachPages'] <= MIN_PAPER_SIZE:
                        continue
                    url = "http://data.eastmoney.com/report/zw_stock.jshtml?encodeUrl=" + \
                          report_data_list[j]['encodeUrl']
                    req = urllib.request.Request(url=url, headers=user_agent)
                    ret = urllib.request.urlopen(req, timeout=200)
                    try:
                        content = ret.read()
                    except Exception as e:
                        content = e.partial  # 防止读到不全的链接

                    soup = BeautifulSoup(content, 'lxml')
                    # 找到所有的超链接，然后找到a的子链接是带有pdf前缀的
                    for a in soup.findAll('a', href=True):
                        if re.findall('http://pdf', a['href']):
                            publish_date = report_data_list[j]['publishDate'][:10].replace('-', '')
                            stock_name = remove_special_chars(report_data_list[j]['stockName'])
                            org_name = report_data_list[j]['orgSName']
                            title = remove_special_chars(report_data_list[j]['title'])
                            pages_num = report_data_list[j]['attachPages']
                            download_list.append(a['href'])
                            file_path = 'report/{}_{}/'.format(stock_name, str(stk_id))
                            file_name = '{}_{}_{}_{}({}).pdf'.format(publish_date, org_name, stock_name, title,
                                                                     pages_num)

                            # 检测是否为空
                            if not os.path.exists(file_path):
                                os.mkdir(file_path)
                            # 检测是否已经有该文件
                            if os.path.exists(file_path + file_name):
                                logger.info(file_name + '已存在')
                                break
                            else:
                                # print('downloading', publish_date, title)
                                # print('=============')
                                urllib.request.urlretrieve(a['href'], file_path + file_name)
                                logger.info(file_name + ' downloaded')
                            break
        except Exception as e:
            logger.error(stk_id + ':' + str(e))


if __name__ == '__main__':
    download_paper(use_proxy=True)
