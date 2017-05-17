#!/usr/bin python
#-*-coding:utf-8-*-

import argparse
import os
import commands
import time


#获取参数列表
def getArgs():
    parse=argparse.ArgumentParser()
    parse.add_argument('-U',type=str,default="http://192.168.1.213:5013",help="指定base url")
    parse.add_argument('-B',type=str,default="",help="指定获取bamboo json文件路径，以逗号分隔")
    parse.add_argument('-H',type=str,default="",help="指定获取haproxy json文件路径,以逗号分隔")
    parse.add_argument('-A',type=str,default="",help="指定获取app json文件路径,以逗号分隔")
    return parse.parse_args()


#发布应用
def deployApp(jFileList,token,baseurl):
    for i in jFileList:
        if os.path.exists(i):
            getJsonCmd =  r'cat ' + i
            (status,json) = commands.getstatusoutput(getJsonCmd)
            if status == 0:
                callAPICmd = r"curl -X POST -H 'Authorization: " + token + r"' " + baseurl + r"/v1/apps -d '" + json + r"'"
                print(callAPICmd)
                (status,result) = commands.getstatusoutput(callAPICmd)
                if status == 0:
                    print("result is: %s" % result)
            else:
            print("exec %s Error: %s" % (getJsonCmd,result))
            continue
        else:
                print("exec %s Error: %s" % (getJsonCmd,json))
        continue
        else:
            print("%s file not exist!" % i)
        continue
        time.sleep(5)


if __name__=='__main__':
    args=getArgs()
    bamboos=args.B
    haproxys=args.H
    apps=args.A
    baseurl=args.U

    #获取token，若获取失败退出
    getTokenCmd = r'sh get_token.sh'
    (status,token) = commands.getstatusoutput(getTokenCmd)
    if status != 0:
        print("execution %s Error: %s" % (getTokenCmd,token) )
        os._exit(0)
    else:
    #发布bamboo
        if len(bamboos) != 0:
            bambooList = bamboos.split(",")
            deployApp(bambooList,token,baseurl)
        #发布haproxy
    if len(haproxys) != 0:
            haproxyList = haproxys.split(",")
            deployApp(haproxyList,token,baseurl)
    #发布app
        if len(apps) != 0:
            appList = apps.split(",")
            deployApp(appList,token,baseurl)