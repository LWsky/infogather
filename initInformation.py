#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import subprocess

def check_services():
    services_status = {} #1:启动  0:关闭
    isredis = os.popen("ps -ef|grep redis | grep -v grep").readlines()
    isjava = os.popen("ps -ef|grep java | grep -v grep").readlines()
    ismysql = os.popen("ps -ef|grep mysqld | grep -v grep").readlines()
    if isjava:
        services_status['java'] = 1
    else:
        services_status['java'] = 0
    if isredis:
        services_status['redis'] = 1
    else:
        services_status['redis'] = 0
    if ismysql:
        services_status['mysql'] = 1
    else:
        services_status['mysql'] = 0
    return services_status

def check_jkd_version():
    v_content = subprocess.Popen(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    v = v_content.communicate()[1].split("\n")[0]
    if "1.8" in v:
        return 1