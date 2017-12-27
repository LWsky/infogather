#!/usr/bin/python
# -*- coding:utf-8 -*-

import os

def check_services():
    services_status = {} #1:启动  0:关闭
    isredis = os.popen("ps -ef|grep redis | grep -v grep").readlines()
    if isredis:
        services_status['redis'] = 1
    else:services_status['redis'] = 0
    return services_status