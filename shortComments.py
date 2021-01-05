# -*- coding: utf-8 -*-
# @ProjectName: doubanCrawler
# @File: shortComments.py
# @Author: Lyn
# @Date: 2021/1/5 12:01
# @IDE: PyCharm
# @Version: 1.0
# @Function: 获取豆瓣电影短评

from selenium import webdriver
import pandas as pd


URL = 'https://movie.douban.com/subject/26266893/comments?status=P'
driver = webdriver.Chrome()
driver.get(URL)
