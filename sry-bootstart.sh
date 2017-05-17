#!/bin/sh

PWD=`pwd`

#check dnsmasq wethere start
PID=`ps -ef | grep "dnsmasq" | grep -v "grep" | awk '{print $2}'`
if [ -z $PID ]; then
    #start dnsmasq
    systemctl start dnsmasq.service
else
    echo "dnsmasq.service had started"
fi

#check docker wethere start
DOCKERPID=`ps -ef | grep "docker.sock" | grep -v "grep" | awk '{print $2}'`
if [ -z $DOCKERPID ]; then
    #start docker
    systemctl start docker.service
else
    echo "docker.service had started"
fi


#define sry-services list
ServicesList=("dataman-mola" "dataman-monitor-grafana" "dataman-monitor-prometheus" "dataman-monitor-alertmanager"  
"dataman-monitor-consul-exporter" "dataman_logstash_1" "dataman_kibana_1" "dataman_elasticsearch_1" "dataman-registry"  
"dataman-log-agent" "dataman-mesos-slave" "dataman-borgsphere" "dataman-marathon" "dataman-mesos-master"  
"dataman-zookeeper" "dataman-mysql" "dataman-cadvisor" "dataman-consul-master" "offline_registry_1")

ServicesListLen=${#ServicesList[@]}-1

#just sry-services wethere has started
containerNums=`docker ps | awk '{print $1}'`
if [ "$containerNums" != "CONTAINER" ]; then
    #waiting 2 min to stop sry-services
    sleep 120
    for ((i=0;i<=$ServicesListLen;i++));
    do
        docker stop ${ServicesList[$i]} > /dev/null
        echo "${ServicesList[$i]} has stop"
    done
fi
#start sry-services
for ((i=$ServicesListLen;i>=0;i--));
do
    docker start ${ServicesList[$i]} > /dev/null
    echo "${ServicesList[$i]} has start"
    sleep 5
done
