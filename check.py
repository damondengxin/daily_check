#!/usr/bin/env /proj/sh/daily_check_py/env/bin/python

import sys,os
import paramiko
import xlwt
import time
from datetime import datetime
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import  MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import  parseaddr,formataddr
import traceback
from email.header import  Header
import zipfile 
from zipfile import *


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    filename='check.log',
                    filemode='w',
                    datefmt='%Y-%m-%d %X')

def header(work_sheet):
    work_sheet.write(0, 0, '检查项目', style0)
    work_sheet.write(0, 1, '命令', style0)
    work_sheet.write(0, 2, '检查结果', style0)
    work_sheet.write(0, 3, '检查主机', style0)
    logging.info('header add ok!')
    return work_sheet



def run_host_cmd(host, work_sheet):
    ssh = paramiko.SSHClient()
    with open('./hosts/' + 'common.cmd') as f1:
        for line in f1.readlines():
            rows = len(work_sheet.rows)
            line = line.strip()
            if line == '':
                continue
            items = line.split(':')
            check_type = items[0]
            check_cmd = items[1]
            work_sheet.write(rows, 0, check_type)
            work_sheet.write(rows, 1, check_cmd)
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh.connect(host)
            except Exception as e:
                logging.error('can not connect host: ' + host)
                logging.error('command can not exec: ' + check_cmd)
                logging.error(e)
                continue
            stdin, stdout, stderr = ssh.exec_command(check_cmd)
            work_sheet.write(rows, 2, stdout.read().decode())
            work_sheet.write(rows, 3, host)
    with open('./hosts/' + host + '.cmd') as f2:
        for line in f2.readlines():
            rows = len(work_sheet.rows)
            line = line.strip()
            if line == '':
                continue
            items = line.split(':')
            check_type = items[0]
            check_cmd = items[1]
            work_sheet.write(rows, 0, check_type)
            work_sheet.write(rows, 1, check_cmd)
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh.connect(host)
            except Exception as e:
                logging.error('can not connect host: ' + host)
                logging.error('command can not exec: ' + check_cmd)
                logging.error(e)
                continue
            stdin, stdout, stderr = ssh.exec_command(check_cmd)
            work_sheet.write(rows, 2, stdout.read().decode())
            work_sheet.write(rows, 3, host)

    ssh.close()
    return work_sheet
#def compact():

def send_mail():
    daytime= time.strftime('%Y-%m-%d', time.localtime(time.time()))
    compactname='report' + daytime + '.zip'
    f=zipfile.ZipFile(compactname,'w',zipfile.ZIP_DEFLATED)
    startdir = "./report"
    for dirpath,dirnames,filenames in os.walk(startdir):
        for filename in filenames:
            f.write(os.path.join(dirpath,filename))
    f.close
    mail_host="smtp.exmail.qq.com"
    mail_user = 'admin@qq.com'
    mail_pass = '123456'
    sender = "admin@qq.com"
    recerviers = ['test1@qq.com','test2@qq.com']
    message = MIMEMultipart()
    message['From'] = Header("%s" %(sender))
    message['To'] = Header("平台巡检")
    message['Subject'] = Header('巡检报告')
    #邮件正文
    message.attach(MIMEText('巡检报告','plain','utf-8'))
    #邮件附件
    att1=MIMEApplication(open(compactname,'rb').read())
    att1.add_header('Content-Disposition','attachment',filename=compactname)
    message.attach(att1)

    #发送
    try:
        smtpobj= smtplib.SMTP(mail_host)
        smtpobj.login(mail_user,mail_pass)
        smtpobj.sendmail(sender,recerviers,message.as_string())
        print('mail send success')
    except smtplib.SMTPException:
        print('error,发送失败')

if __name__ == '__main__':

    with open('./hosts/host.info','r') as hosts_file:
        for line in hosts_file.readlines():
            if line[0:1] == '#': continue
            host = line.strip()
            #items = line.split()
            #port = 22
            #host = items[0]
            #print(host)
            #print('###')
            #username = items[1]
            #password = items[2]
            style0 = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;' +
                         'font: name Times New Roman, color-index black, bold on;' +
                         'borders: left thick, right thick, top thick, bottom thick;' +
                         'align: horiz center',
                         num_format_str='0,000.00')
            work_book = xlwt.Workbook()
            work_sheet = work_book.add_sheet('Sheet1')
            work_sheet = header(work_sheet)
            work_sheet = run_host_cmd(host, work_sheet)
            logging.info(host + ' check finish !\n')
            file_pre = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            filereport=host +'_' + file_pre + '.xls'
            work_book.save(filereport)
            os.system("mv %s ./report" %(filereport))

    #compact()
    send_mail()

