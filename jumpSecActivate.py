#!/usr/bin/python
#-*-coding:utf-8-*-

import argparse
import os
import commands
import string
import shutil


#获取参数列表
def getArgs():
    parse=argparse.ArgumentParser()
    parse.add_argument('-U',type=str,default="",help="指定用户列表，以逗号分隔")
    parse.add_argument('-J',type=str,default="",help="指定跳板机列表,以逗号分隔;主要跳板机列表:gongsijump,\
    utestjump,qelk,usrydemo,qjump,ujump,ubasicjump,yndw,hwjenkins,jumpall,ujiufu,usingle-new,dmproxy,udemojump,\
    jumpserver,offlinejump")
    parse.add_argument('-S',type=str,default="",help="指定赋予sudo权限用户列表,以逗号分隔")
    parse.add_argument('-T',type=str,default="false",help="指定是否生成证书,此参数默认即可.")
    return parse.parse_args()


#调用生成证书脚本
def genCertFun(users):
    #获取当前目录
    cDir = os.getcwd()
    #在生成新证书文件前，先清理private目录
    privateDir = cDir + r'/secretkey/private/'
    if os.path.exists(privateDir):
        shutil.rmtree(privateDir)
    #切换到生成密钥目录
    genCertDir = cDir + r'/secretkey/code/'
    #调用生成证书脚本
    genCertCmd = r'cd  ' + genCertDir + r';python new_sshkey.py -U ' + users + r';cd ' + cDir
    (status,genCertRes) = commands.getstatusoutput(genCertCmd)
    if status == 0 :
        print("%s" % genCertRes)
    else:
        print("execution %s command Error: %s" % (genCertCmd,genCertRes))
        os._exit(0)


#同步公钥
def syncCertFile():
    #获取当前目录
    cDir = os.getcwd()
    #证书生成目录
    privateDir = cDir + r'/secretkey/private/'
    #跳板机权限公共密钥路径
    pubCertDir = cDir + r'/roles/user-mgt/files/'
    cpPubCertCmd = r'\cp ' + privateDir + "*.pub " + pubCertDir
    (status,cpPubCertRes) = commands.getstatusoutput(cpPubCertCmd)
    if status != 0 :
        print("execution %s command Error: %s" % (cpPubCertCmd,cpPubCertRes))
        os._exit(0)
    

#git pull
def gitPullFun():
    gitPullCmd = r'git pull origin master'
    (status,gitPullRes) = commands.getstatusoutput(gitPullCmd)
    if status == 0 :
        print("%s" % gitPullRes)
    else:
        print("execution %s command Error: %s" % (gitPullCmd,gitPullRes))
        os._exit(0)


#git push
def gitPushFun(users):
    cDir = os.getcwd()
    pubCertDir = cDir + r'/roles/user-mgt/files/'
    userList = users.split(",")
    commitFiles = '.pub '.join(userList) + r'.pub ../../../secretkey/passwd.txt' 
    print(commitFiles)
    #切换路径
    if os.path.exists(pubCertDir):
        os.chdir(pubCertDir)
    else:
        print("%s dir not exist" % pubCertDir)
        os._exit(0)
    gitAddCmd = r'git add ' + commitFiles
    (status,gitAddRes) = commands.getstatusoutput(gitAddCmd)
    if status == 0 :
        print("%s" % gitAddRes)
    else:
        print("execution %s command Error: %s" % (gitAddCmd,gitAddRes))
        os._exit(0)
    gitCommitCmd = r'git commit -m ' + r'"add ' + commitFiles + r'"'
    (status,gitCommitRes) = commands.getstatusoutput(gitCommitCmd)
    if status == 0 :
        print("%s" % gitCommitRes)
    else:
        print("execution %s command Error: %s" % (gitCommitCmd,gitCommitRes))
        os._exit(0)
    gitPushCmd = r'git push -u origin master'
    (status,gitPushRes) = commands.getstatusoutput(gitPushCmd)
    if status == 0 :
        print("%s" % gitPushRes)
    else:
        print("execution %s command Error: %s" % (gitPushCmd,gitPushRes))
        os._exit(0)
    os.chdir(cDir)

#判断是否已存在某个用户的公共证书
def justPubCert(users):
    userList = users.split(",")
    cDir = os.getcwd()
    pubCertDir = cDir + r'/roles/user-mgt/files/'
    #切换路径
    if os.path.exists(pubCertDir):
        os.chdir(pubCertDir)
    else:
        print("%s dir not exist" % pubCertDir)
        os._exit(0)
    newUsers = ""
    for uname in userList:
        relUname = uname + r'.pub'
        if not os.path.exists(relUname):
            newName = uname + ',' 
            newUsers += newName 
    os.chdir(cDir)
    if newUsers != "":
        newUsers = newUsers[:len(newUsers)-1]
        genCertFun(newUsers)
        syncCertFile()
        gitPushFun(newUsers)
    

#开通跳板机权限
def jumpActiveFun(users,jumps,sudoUsers):
    exportEnvCmd = r'export ANSIBLE_SCP_IF_SSH=y'
    (status,exportEnvRes) = commands.getstatusoutput(exportEnvCmd)
    if status != 0 :
        print("execution %s command Error: %s" % (exportEnvCmd,exportEnvRes))
        os._exit(0)
    jumpList = jumps.split(",")
    userList = str(users.split(",")).replace("'",'"').replace(" ","")
    if sudoUsers != "":
        sudoUserList = str(sudoUsers.split(",")).replace("'",'"').replace(" ","")
    else:
        sudoUserList = r'[]'
    for jumpName in jumpList:
        secActiveCmd = r"ansible-playbook -vvvv playbooks/user-mgt/user-mgt.yml  --extra-vars 'hosts=" + jumpName + r" userlist=" + userList + r" wheelusers=" + sudoUserList + r"'"
        (status,secActiveRes) = commands.getstatusoutput(secActiveCmd)
        if status == 0 :
            print("%s" % secActiveRes)
        else:
            print("execution %s command Error: %s" % (secActiveCmd,secActiveRes))
            continue


if __name__=='__main__':
    args=getArgs()
    users=args.U
    jumps=args.J
    sudoUsers=args.S
    genCertFlag = args.T
    #判断生成证书的用户列表是否为空，为空退出，需要通过-U制定用户列表
    if users != "" or jumps != "":
        gitPullFun()
        #如果生成证书的flag是true，则调用生成证书的函数
        if genCertFlag == "true": 
            genCertFun(users)
            syncCertFile()
            gitPushFun(users)
        else:
            justPubCert(users)
        jumpActiveFun(users,jumps,sudoUsers)
    else:
        print("用户列表,跳板机列表均不能为空，请使用-U指定用户列表，-J制定跳板机列表!")
        os._exit(0) 
