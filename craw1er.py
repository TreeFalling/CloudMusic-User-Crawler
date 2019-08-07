# -*- coding:utf-8 -*-
from concurrent import futures  #使用该模块实现进程池，用于编写异步多进程爬虫
from selenium import webdriver  #模拟用户使用浏览器过程，动态抓取网页内容
from bs4 import BeautifulSoup   #处理html信息
import xlwt                     #写入数据至Excel

def beautiful_new_world(num):
    #创建.xls文件
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet(str(num) + '~' + str(num+100), cell_overwrite_ok=True)

    #爬虫函数(每个进程最多爬200个id，此处可自行调整
    for user_id in range(num,  num+200):
        #动态抓取并解析网页内容
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        url = 'https://music.163.com/#/user/home?id=' + str(user_id)
        driver = webdriver.Chrome(r"C:\chromedriver\chromedriver.exe", options=option)
        driver.get(url)
        driver.switch_to.frame('g_iframe')
        web_data = driver.page_source
        soup = BeautifulSoup(web_data, 'lxml')

        #用户年龄
        for k in soup.find_all('span', class_='sep', id='age'):
            a = k.find_all('span')
            if a:
                sheet.write(int(user_id)-num+1, 1, a[0].string)
            else:
                sheet.write(int(user_id)-num+1, 1, 'NONE')

        #用户地区
        for j in soup.find_all('div', class_='inf s-fc3'):
            e = j.find_all('span')
            if e:
                sheet.write(int(user_id)-num+1, 2, e[0].string[5:])
            else:
                sheet.write(int(user_id)-num+1, 2, 'NONE')

        #用户性别
        for link in soup.find_all("i"):
            if link.get("class") == ['icn', 'u-icn', 'u-icn-01']:
                sheet.write(int(user_id)-num+1, 3, '男')
                break
            elif link.get("class") == ['icn', 'u-icn', 'u-icn-02']:
                sheet.write(int(user_id)-num+1, 3, '女')
                break
            else:
                sheet.write(int(user_id)-num+1, 3, 'NONE')

        #用户听歌排行榜前十首
        col = 4 #Excel对应列数
        for l in soup.find_all('span', class_='txt'):
            song_name = l.find_all('b')
            song_author = l.find_all('a', class_='s-fc8')
            if song_name and song_author:
                song = song_name[0].string + '-' + song_author[0].string
                sheet.write(int(user_id)-num+1, col, song)
            else:
                sheet.write(int(user_id)-num+1, col, 'NONE')
            col = col + 1 #下一列

        #网易云音乐用户id分布为非连续
        #通过跳过整块的空白id群实现信息过滤与速度提升
        flag = 1
        for x in soup.find_all('div', class_='n-for404'):
            key = x.find_all('p')
            if key[0].string == '很抱歉，你要查找的网页找不到':
                flag = 0

        driver.__exit__() #关闭当前界面
        workbook.save(str(num) + '.xls') #保存文件
        if flag == 0: break #跳出循环以跳过空白id群
#data里请放入间隔为200的id，下面为实例
data=[1001, 1201, 1401
]
#创建进程池并设置最大同时运行数
with futures.ThreadPoolExecutor(max_workers=5) as executor:
    for future in executor.map(beautiful_new_world, data):
        print('Mission accomplished') #一个进程完成以后的提示