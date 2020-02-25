from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium.webdriver.common.action_chains import ActionChains
import cv2
import random

def get_gap():
    yanzheng = cv2.imread('img.png', 0)
    _, thre = cv2.threshold(yanzheng, 254, 255, 0)
    for i in range(0, thre.shape[0]):
        for j in range(40, thre.shape[1]):
            if thre[i][j] == 255:
                return j+20   #加20左右差不多是正好的移动，直接用j会少一点


def log_in(broser, usrname, passport):

    #找到网址输入账号密码
    broser.get('http://sfrz.cug.edu.cn/tpass/login?service=http%3A%2F%2Fxyfw.cug.edu.cn%2Ftp_up%2F')
    broser.maximize_window()
    broser.find_element_by_css_selector('#login_content #un').send_keys(usrname)
    broser.find_element_by_css_selector('#login_content #pd').send_keys(passport)

    #截屏存储验证码
    img = broser.find_element_by_css_selector('#mpanel4 .verify-img-panel')
    img.screenshot('img.png')

    #判断缺口的x位置
    ball = broser.find_element_by_css_selector('.verify-bar-area .verify-left-bar .verify-move-block')
    xoff = get_gap()
    ActionChains(broser).click_and_hold(ball).perform()
    ActionChains(broser).move_to_element_with_offset(ball, xoffset=xoff, yoffset=0).perform()
    ActionChains(broser).release(ball).perform()

    #找到登录按钮并点击
    broser.find_element_by_css_selector('.landing_btn_bg #index_login_btn').click()
    time.sleep(3)
    return broser


def to_502(log_in_page):
    #找到地大教务系统
    log_in_page.find_element_by_css_selector(".bar .integration div[title='502-教务管理系统']").click()
    windows = log_in_page.current_window_handle #定位当前页面句柄
    all_handles = log_in_page.window_handles   #获取全部页面句柄
    for handle in all_handles:          #遍历全部页面句柄
        if handle != windows:          #判断条件
            log_in_page.switch_to.window(handle)      #切换到新页面
    time.sleep(1)
    cookies = log_in_page.get_cookies()
    cookistr = cookies[0]['value']
    return cookistr, log_in_page


def get_achivement(cookistr, year, month, print_or_save):
    #get achivement
    cj_url = 'http://202.114.207.126/jwglxt/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005'
    headers = {}
    headers['Cookie'] = 'JSESSIONID=' + str(cookistr)
    formdata = {
        'xnm': year,   #年
        'xqm': month,        #上半学期是3， 下半学期是12
        '_search': 'false',
        'nd': '1580870641226',
        'queryModel.showCount': '15',
        'queryModel.currentPage': '1',
        'queryModel.sortName': '',
        'queryModel.sortOrder': 'asc',
        'time': '0'
    }
    cj_response = requests.post(cj_url, headers=headers, data=formdata)
    soup_cj = BeautifulSoup(cj_response.text, 'html.parser')
    txt = soup_cj.text
    names = re.findall(r'\"kcmc.+?\,', txt)
    score = re.findall(r'\"bfzcj.+?\,', txt)

    achiv = {}
    for i in range(len(names)):
        achiv[names[i].split(':')[-1][:-1].replace('"', '')] = score[i].split(':')[-1][:-1].replace('"', '')
    finall = json.dumps(achiv, ensure_ascii=False)

    if not print_or_save:
        with open('cj.json', 'w', encoding='utf-8') as f:
            f.write(finall)
    else:
        print(finall)


def get_course(broser, usrname, print_or_save):
    #get course
    course_url = 'http://202.114.207.126/jwglxt/kbcx/xskbcx_cxXskbcxIndex.html?gnmkdm=N2151&layout=default&su=' + usrname
    broser.get(course_url)
    time.sleep(5)
    soup_course = BeautifulSoup(broser.page_source, 'html.parser')
    text = soup_course.find('div', id='table2').text
    if not print_or_save:
        with open('course.txt', 'w', encoding='utf-8') as f:
            f.write(text.replace('星', '\n'))
    else:
        print(text.replace('星', '\n'))


def Auto_Evaluation(broser, usrname):
    url = 'http://202.114.207.126/jwglxt/xspjgl/xspj_cxXspjIndex.html?doType=details&gnmkdm=N401605&layout=default&su=' + usrname
    broser.get(url)
    soup = BeautifulSoup(broser.page_source, 'html.parser')
    course_number = len(soup.find_all('tr', role='row'))
    time.sleep(1)
    for i in range(1, course_number):
        try:
            tag_name = '//*[@id="'+str(i) + '"]'
            element = broser.find_element_by_xpath(tag_name)
            ActionChains(broser).move_to_element(element).click(element).perform()
            time.sleep(2)
            broser.find_elements_by_xpath('//*[@id="ajaxForm1"]/div[2]/div[1]/div[2]/table[1]/tbody/tr/td[2]/div/div[1]/label/input')[0].click()
            time.sleep(0.4)
            for i in range(1, 3):
                xpath = '//*[@id="ajaxForm1"]/div[2]/div[1]/div[2]/table[2]/tbody/tr[' + str(i) + ']/td[2]/div/div[' + str(random.choice([1, 2])) + ']'
                broser.find_elements_by_xpath(xpath)[0].click()
                time.sleep(0.4)
            for i in range(1, 4):
                xpath = '//*[@id="ajaxForm1"]/div[2]/div[1]/div[2]/table[3]/tbody/tr[' + str(i) + ']/td[2]/div/div[' + str(random.choice([1, 2])) + ']'
                broser.find_elements_by_xpath(xpath)[0].click()
                time.sleep(0.4)
            for i in range(1, 4):
                xpath = '//*[@id="ajaxForm1"]/div[2]/div[1]/div[2]/table[4]/tbody/tr[' + str(i) + ']/td[2]/div/div[' + str(random.choice([1, 2])) + ']'
                broser.find_elements_by_xpath(xpath)[0].click()
                time.sleep(0.4)
            for i in range(1, 3):
                xpath = '//*[@id="ajaxForm1"]/div[2]/div[1]/div[2]/table[5]/tbody/tr[' + str(i) + ']/td[2]/div/div[' + str(random.choice([1, 2])) + ']'
                broser.find_elements_by_xpath(xpath)[0].click()
                time.sleep(0.4)

            xpath = '//*[@id="ajaxForm1"]/div[2]/div[1]/div[2]/table[6]/tbody/tr/td[2]/div/div[' + str(random.choice([1, 2])) + ']'
            broser.find_elements_by_xpath(xpath)[0].click()
            save_xpath = '//*[@id="btn_xspj_tj"]'
            broser.find_elements_by_xpath(save_xpath)[0].click()
            time.sleep(1)
            broser.find_elements_by_xpath('//*[@id="btn_ok"]')[0].click()
        except:
            continue
      




def main():
    usrname = str(input('你的学号：'))
    passport = str(input('密码：'))
    broser = webdriver.Chrome(executable_path='D:\holiday\python1\chromedriver.exe')
    log_in_page = log_in(broser, usrname, passport)
    cookiestr, page_502 = to_502(log_in_page)
    running = True
    while running:
        try:
            print('你想要干啥！\n')
            number = int(input('1:保存你的成绩\n2:打印你的成绩\n3:保存你的课表\n4:打印你的课表\n5:自动评价\n'))
            if number == 1:
                print_or_save = False
                year = str(input('你要查询的年份:'))
                month = str(input('你要查询的月份（上半年3，下半年12）:'))
                get_achivement(cookiestr, year, month, print_or_save)
            elif number == 2:
                year = str(input('你要查询的年份:'))
                month = str(input('你要查询的月份（上半年3，下半年12）:'))
                print_or_save = True
                get_achivement(cookiestr, year, month, print_or_save)
            elif number == 3:
                print_or_save = False
                get_course(page_502, usrname, print_or_save)
            elif number == 4:
                print_or_save = True
                get_course(page_502, usrname, print_or_save)
            elif number == 5:
                Auto_Evaluation(broser, usrname)
            else:
                print('请善待这玩意，输入错了！')

            close_or_not = str(input('按0退出！别的继续\n'))
            if close_or_not == '0':
                running = False

        except:
            print('出错了嗷')
            running = False


    
if __name__ == "__main__":
    main()
