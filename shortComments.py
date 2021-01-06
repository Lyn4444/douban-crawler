# -*- coding: utf-8 -*-
# @ProjectName: doubanCrawler
# @File: shortComments.py
# @Author: Lyn
# @Date: 2021/1/5 12:01
# @IDE: PyCharm
# @Version: 1.0
# @Function: 获取豆瓣电影短评

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time


def getUserData(url):
    """
    :param url
    :return: userInfo
    """
    time.sleep(1)
    Cookie_str = 'll="118281"; bid=zkdKY0k9vjs; dbcl2="229719978:dmnBNQ/KSE0"; push_noty_num=0; push_doumail_num=0; __utmv=30149280.22971; gr_user_id=04b36935-6824-41f3-881c-4ce9fa1ba388; _vwo_uuid_v2=DDE6AB83892CFEDFBF673F07B0ECD60AA|0e102c6de0f491e988ca37a52307f588; __utmz=30149280.1609841938.5.2.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmz=223695111.1609841953.5.2.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/search; ck=Fh5V; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1609910893%2C%22https%3A%2F%2Fwww.douban.com%2Fsearch%3Fsource%3Dsuggest%26q%3D%25E6%25B5%2581%25E6%25B5%25AA%25E5%259C%25B0%25E7%2590%2583%22%5D; _pk_ses.100001.4cf6=*; ap_v=0,6.0; __utma=30149280.1480719386.1609745412.1609863878.1609910893.8; __utmb=30149280.0.10.1609910893; __utmc=30149280; __utma=223695111.1433316309.1609745540.1609863878.1609910893.8; __utmb=223695111.0.10.1609910893; __utmc=223695111; _pk_id.100001.4cf6=5bca1f7682d412e6.1609745540.8.1609911367.1609865508.'
    Cookie = {}
    for i in Cookie_str.split(';'):
        key, value = i.split('=', 1)
        Cookie[key] = value
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
    userData = requests.get(url, headers=headers, cookies=Cookie)
    userDataSoup = BeautifulSoup(userData.text, 'html.parser')
    user_info = userDataSoup.find_all('div', class_="user-info")
    user_location = ''
    user_date = ''
    try:
        user_location = user_info[0].a.get_text()
    except AttributeError:
        pass
    try:
        user_date = user_info[0].div.get_text().split(' ')[-1][: -2]
    except AttributeError:
        pass
    userInfo = {
        'user_location': user_location,
        'user_date': user_date
    }
    return userInfo


if __name__ == '__main__':
    URL = 'https://movie.douban.com/subject/26266893/comments?status=P'
    driver = webdriver.Chrome()
    driver.get(URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    comment_item = soup.find_all('div', class_="comment-item")
    for comment in comment_item:
        userNameUrl = comment.a['href']
        print(userNameUrl)
        userLocation = ''
        userDate = ''
        try:
            userInfo = getUserData(userNameUrl)
            userLocation = userInfo['user_location']
            userDate = userInfo['user_date']
        except IndexError as e:
            pass
        userName = comment.a['title']
        shortComment = comment.p.find_all('span')[0].string
        score = ""
        try:
            score = str(comment.h3.find_all('span')[-2]['class'][0][-2])
        except KeyError as e:
            score = "0"
        date = str(comment.h3.find_all('span')[-1].string).strip()
        voteCount = str(comment.h3.find_all('span')[1].string)
        shortCommentData = pd.DataFrame({
            'userName': userName,
            'userLocation': userLocation,
            'userDate': userDate,
            'shortComment': shortComment,
            'score': score,
            'date': date,
            'voteCount': voteCount
        }, index=[0])
        print(shortCommentData)
