#!/usr/bin python
#-*-coding:utf-8-*-


import os
import paramiko
import argparse


#获取参数列表
def getArgs():
    parse=argparse.ArgumentParser()
    parse.add_argument('-ip',type=str,default="",help="指定获取ip列表，以逗号分隔")
    parse.add_argument('-u',type=str,default="centos",help="指定登录远程主机用户名")
    parse.add_argument('-p',type=str,default="MbZ6lDw9W3",help="指定私钥证书密码")
    parse.add_argument('-f',type=str,default="~/yhchen",help="指定私钥文件路径")
    return parse.parse_args()

#ssh config modify
def sshModifyFun(ipList,user,pwd,certFile):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    keyfile = os.path.expanduser(certFile)
    key = paramiko.RSAKey.from_private_key_file(keyfile, password=pwd)
    for server in ipList:
        ssh.connect(hostname = server, username = user, pkey = key)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('sudo sed -i "s/PasswordAuthentication no/PasswordAuthentication yes/g" /etc/ssh/sshd_config ;sudo sed -i "s/#PasswordAuthentication yes/PasswordAuthentication yes/g" /etc/ssh/sshd_config ; sudo sed -i "s/#PermitRootLogin yes/PermitRootLogin yes/g" /etc/ssh/sshd_config; sudo systemctl restart sshd',get_pty=True) 
        print "stdout:"
        print ssh_stdout.readlines()
        print "stderr:"
        print ssh_stderr.readlines()

if __name__=='__main__':
    args=getArgs()
    ipStr=args.ip
    user=args.u
    pwd=args.p
    certFile=args.f
    #判断ip列表是否为空，为空则需要使用-ip指定ip列表
    if ipStr != "":
        #调用sshModifyFun
        ipList = ipStr.split(",")
        sshModifyFun(ipList,user,pwd,certFile)
    else:
        print("ip列表不能为空，请使用-ip指定ip列表")
        os._exit(0)
