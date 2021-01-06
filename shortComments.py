# -*- coding: utf-8 -*-
# @ProjectName: doubanCrawler
# @File: shortComments.py
# @Author: Lyn
# @Date: 2021/1/5 12:01
# @IDE: PyCharm
# @Version: 1.0
# @Function: 获取豆瓣电影短评

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import time

Cookies_str = ''
pageCookies = {}


def initCookie():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get('https://www.douban.com/')
    time.sleep(6)
    driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="anony-reg-new"]/div/div[1]/iframe'))
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[1]/a[1]').click()
    time.sleep(10)
    dictCookies = driver.get_cookies()
    jsonCookies = json.dumps(dictCookies)
    with open('cookies.txt', 'w') as f:
        f.write(jsonCookies)


def login():
    for k_v in Cookies_str.split(';'):
        k, v = k_v.split('=', 1)
        pageCookies[k.strip()] = v.replace('"', '')

    URL = 'https://movie.douban.com/subject/26266893/comments?start=20&limit=20&status=P&sort=new_score'
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(URL)
    with open('cookies.txt', 'r', encoding='utf8') as f:
        listCookies = json.loads(f.read())
    for cookie in listCookies:
        cookie_dict = {
            'domain': '.douban.com',
            'name': cookie.get('name'),
            'value': cookie.get('value'),
            "expires": '',
            'path': '/',
            'httpOnly': False,
            'HostOnly': False,
            'Secure': False
        }
        driver.add_cookie(cookie_dict)
    driver.refresh()
    return driver


def getUserData(url):
    """
    :param url
    :return: userInfo
    """
    time.sleep(1)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    userData = requests.get(url, headers=headers, cookies=pageCookies)
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


def getPageData(strPage):
    """
    :param strPage
    :return: pageShortCommentData
    """
    soup = BeautifulSoup(strPage, "html.parser")

    comment_item = soup.find_all('div', class_="comment-item")
    pageShortCommentData = pd.DataFrame()
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
            '用户名': userName,
            '地址': userLocation,
            '加入时间': userDate,
            '短评': shortComment,
            '评分': score,
            '发表时间': date,
            '获赞数': voteCount
        }, index=[0])
        pageShortCommentData = pageShortCommentData.append(shortCommentData)
    return pageShortCommentData


def getAllData():
    """

    :rtype: object
    """
    driver = login()
    allData = pd.DataFrame()
    wait = WebDriverWait(driver, 10)
    while True:
        wait.until(
            ec.element_to_be_clickable(
                (By.CSS_SELECTOR, '#comments > div:nth-child(4) > div.comment > h3 > span.comment-info > a')
            )
        )

        pageData = getPageData(driver.page_source)
        allData = allData.append(pageData)
        if not driver.find_element_by_css_selector('#paginator > a'):
            break

        confirm = wait.until(
            ec.element_to_be_clickable(
                (By.CSS_SELECTOR, '#paginator > a')
            )
        )

        confirm.click()
        print(len(allData))
    return allData


if __name__ == '__main__':
    initCookie()
    AllData = getAllData()
    AllData.to_csv('allData.csv', index=0)
