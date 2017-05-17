#!/usr/bin python
#-*-coding:utf-8-*-

import argparse
import os
import commands


#获取参数列表
def getArgs():
    parse=argparse.ArgumentParser()
    parse.add_argument('-D',type=str,default="borgsphere",help="指定获取tag各个项目的源码目录名，以逗号分隔")
    parse.add_argument('-K',type=str,default="borgsphere",help="指定获取各个项目的imagelist的镜像地址,以逗号分隔")
    return parse.parse_args()


#获取最新tag信息
def getTags(tagList):
    #获取当前offlinesry路径    
    curDir = os.getcwd()
    tags = []
    for i in tagList:
        #拼接目标路径
        tDir = curDir.replace("offlinesry",i) 
        #判断tDir路径是否存在
        if os.path.exists(tDir):    
            os.chdir(tDir)
            cmd = r"git describe --abbrev=0 --tags origin/master"
            tag = commands.getoutput(cmd)
            tags.append(tag)
        else:
            print("%s dir not exist!" % tDir)

    os.chdir(curDir)
    return tags


#生成新的仓库地址
def newRegistryAddr(tagList,keyList,tags):
    tagListLen = len(tagList)
    for i in range(tagListLen):
        #imageslist 镜像url的tag替换
        jqCmd = r'jq .' + keyList[i] + r' imagelist.txt  --raw-output'
        (status,sImageAddr) = commands.getstatusoutput(jqCmd)
        if status == 0 :
            if sImageAddr == "null":
                print("%s key dose not exist!" % keyList[i])
                continue
            #拼接新的imagesList key的value
            tImageAddr = sImageAddr.split(":")[0] + ":" + tags[i]
            #替换imageList key的vlalue
            rplCmd = r'sed -i ' + r's#' + sImageAddr + r'#' + tImageAddr + r'#g imagelist.txt'
            (status,result) = commands.getstatusoutput(rplCmd)
            if status != 0:
                print("execution %s Error: %s" % (rplCmd,result) )
                continue
        else:
            print("execution %s Error: %s" % (jqCmd,sImageAddr))
            continue


if __name__=='__main__':
    args=getArgs()
    tagInfo=args.D
    imagesKey=args.K
    #判断获取tag的目标目录与imagesList的key值得数量是否一致，不一致退出
    tagList = tagInfo.split(",")
    keyList = imagesKey.split(",")
    if len(tagList) == len(keyList):
        tags = getTags(tagList)
        newRegistryAddr(tagList,keyList,tags)
        print("update imagesList finish!")
    else:
        print("获取tag的目标目录与imagesList的key值得数量不一致，请重新重新指定相应参数")
        os._exit(0)
