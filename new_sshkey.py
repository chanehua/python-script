#!/usr/bin/env python
#coding: utf-8
import os
import shutil 
import random
import subprocess
import smtplib
from Crypto.PublicKey import RSA
import argparse

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

BASE_DIR = '../../secretkey'
PRIVATE_DIR = 'private/'
PUBLIC_DIR = 'private/'
#PUBLIC_DIR = 'public/'
RAND_NUM = 10

private_key_dir = os.path.join(BASE_DIR, PRIVATE_DIR)
public_key_dir = os.path.join(BASE_DIR, PUBLIC_DIR)
passwd_file = os.path.join(BASE_DIR, 'passwd.txt')
course_file = BASE_DIR + '/code/course.txt'

emailAccount = 'devops@dataman-inc.com'
emailPasswd = 'operation1234'


class FindError(Exception):
    pass

#获取参数列表
def getArgs():
    parse=argparse.ArgumentParser()
    parse.add_argument('-U',type=str,default="",help="指定获取用户列表，以逗号分隔")
    return parse.parse_args()

def rand_pwd(num):
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    salt_list = []
    for i in range(num):
        salt_list.append(random.choice(seed))
    salt = ''.join(salt_list)
    return salt

def get_mail_content(filename):
    if not os.path.exists(filename):
        print 'Error: file not exists: %s ' % filename
    if not os.path.isfile(filename):
        print 'Error: %s is not a file' % filename

    f = open(filename, 'r')
    content = f.read()
    f.close()
    return content

def gen_ssh_key(username, length=2048):
    private_key_file = os.path.join(private_key_dir, username)
    #private_key_file = os.path.join(private_key_dir, username + '.pri')
    public_key_file = os.path.join(public_key_dir, username + '.pub')

    zip_pwd = rand_pwd(RAND_NUM)
    with open(passwd_file, 'a') as pwdfile:
        pwdfile.write(username + ':       ' + zip_pwd + '\n')
    
    if not os.path.isdir(private_key_dir):
        os.makedirs(private_key_dir)

    if not os.path.isdir(public_key_dir):
        os.makedirs(public_key_dir)

    key = RSA.generate(length)

    with open(private_key_file, 'w') as fprivate:
        fprivate.write(key.exportKey('PEM', zip_pwd))    
    os.chmod(private_key_file, 0600) 

    with open(public_key_file, 'w') as fpublic:
        fpublic.write(key.publickey().exportKey('OpenSSH'))

    p = subprocess.call("/usr/bin/zip -q -r -P %s %s %s" % (zip_pwd, private_key_dir + username + '.zip', private_key_dir), shell=True)
    if p != 0:
        shutil.rmtree(private_key_dir, True)
        #shutil.rmtree(public_key_dir, True)
        raise FindError(u'用户%s密钥生成错误' % username)
    print zip_pwd

def sshkey_sendmail(username):
    msg = MIMEMultipart()
    content = get_mail_content(course_file)
    gen_ssh_key(username) 

    mail_body = MIMEText(content, 'plain', 'utf-8')
    mail_key = MIMEText(open(private_key_dir + username + '.zip', 'rb').read(), 'base64', 'gb2312')  
    mail_key["Content-Type"] = 'application/octet-stream'
    mail_key["Content-Disposition"] = 'attachment; filename="private.zip"'  

    msg.attach(mail_body)
    msg.attach(mail_key)

    msg['to'] = username + '@dataman-inc.com'
    msg['from'] = emailAccount
    msg['subject'] = 'Private key and how to use it'

    try:
        server = smtplib.SMTP()
        server.connect('smtp.exmail.qq.com')
        server.login(emailAccount, emailPasswd)
        server.sendmail(msg['from'], msg['to'], msg.as_string())
        server.quit()
        print '发送成功'
    except Exception, e:
        print str(e)

if __name__ == '__main__':
    args=getArgs()
    users=args.U
    if users != "":
        userList = users.split(",")
        for uname in userList:
           sshkey_sendmail(uname)
    else:
        print("用户列表不能为空，请使用-U指定用户列表!")
        os._exit(0)
