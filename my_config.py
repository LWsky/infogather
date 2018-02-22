#!/usr/bin/python
# -*- coding:utf-8 -*-

import ConfigParser
import os

def getConfig(section,key):
    config = ConfigParser.ConfigParser()
    path =  os.path.split(os.path.realpath(__file__))[0] + '/config/db.conf'
    config.read(path)
    return config.get(section,key)

def getRedisNodes():
    redisHost = getConfig("redisCluster", "host")
    redisPort = getConfig("redisCluster","port")
    redisPassword = getConfig("redisCluster","password")
    redisHosts = redisHost.split(',')
    redisPorts = redisPort.split(',')
    print redisPassword
    print redisHosts
    RedisNodesList = []
    for host,port in zip(redisHosts,redisPorts):
        dict = {}
        dict["host"] = host
        dict["port"] = port
        RedisNodesList.append(dict)
    return RedisNodesList

