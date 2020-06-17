# coding: utf-8
# Author：fengchi863
# Date ：2020/6/17 15:43

from urllib import request
from urllib import error
import json
import os
import requests
import re
from bs4 import BeautifulSoup
import urllib
import socket
import time

timeout = 20
socket.setdefaulttimeout(timeout)  # 这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置
sleep_download_time = 10
time.sleep(sleep_download_time)  # 这里时间自己设定


def readFile(Fname):
    f = open("d:/研报下载/" + Fname + ".txt", "r")
    return f.read()


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"}

s = readFile("test新增").split(",")
for stock in range(len(s)):
    for j in range(1, 10):
        url = "http://reportapi.eastmoney.com/report/list?cb=&pageNo={}&pageSize=80&code={}&industryCode=*&industry=*&rating=*&ratingchange=*&beginTime=2016-1-1&endTime=2017-1-24&fields=&qType=0&_="

        try:
            url_new = url.format(j, s[stock])
            print(url_new)
            req = urllib.request.Request(url_new, headers=headers)
            sout = request.urlopen(req, timeout=200)
            sout = sout.read().decode("utf8")
            # print(sout[0:100])
            for i in range(len(sout)):
                if sout[i:i + 4] == 'data':
                    sout = sout[i:-1]

            sout = '{"' + sout + '}'
            decodejson = json.loads(sout)
            ss = decodejson["data"]

            download_lst = []
            for j in range(0, len(ss)):
                if ss[j]['publishDate'][:10] > '2017-01-26':
                    continue
                # print(ss[j]['encodeUrl'])
                # print(ss[j]['stockName'],ss[j]['title'],ss[j]['encodeUrl'])
                url = "http://data.eastmoney.com/report/zw_stock.jshtml?encodeUrl=" + ss[j]['encodeUrl']
                req = urllib.request.Request(url=url, headers=headers)
                url = urllib.request.urlopen(req, timeout=200)
                content = url.read()
                soup = BeautifulSoup(content, 'lxml')
                flag = 1
                for a in soup.findAll('a', href=True):
                    # print(a)
                    if re.findall('http://pdf', a['href']) and flag == 1:
                        download_lst.append(a['href'])
                        # print ("Found the URL:", a['href'])

                        try:
                            print('downloading', ss[j]['stockName'], ss[j]['title'])
                            # print(ss[j]['stockName'],ss[j]['title'])
                            urllib.request.urlretrieve(a['href'],
                                                       '300347/{}_{}_{}.pdf'.format(ss[j]['publishDate'][:10],
                                                                                    ss[j]['stockName'], ss[j]['title']))
                            flag = 0
                        except:
                            print('wrong')
        except:
            print('error')
            continue