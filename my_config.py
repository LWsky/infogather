#!/usr/bin/python
# -*- coding:utf-8 -*-

import ConfigParser
import os


class MyConfig():
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.split(os.path.realpath(__file__))[0] + '/config/db.conf')

    def getConfig(self,section,key):
        return self.config.get(section,key)

    def getAllSection(self):
        return self.config.sections()

    def getRedisNodes(self):
        redisHost = self.getConfig("redisCluster", "host")
        redisPort = self.getConfig("redisCluster","port")
        redisPassword = self.getConfig("redisCluster","password")
        redisHosts = redisHost.split(',')
        redisPorts = redisPort.split(',')
        #print redisPassword
        #print redisHosts
        RedisNodesList = []
        for host,port in zip(redisHosts,redisPorts):
            dict = {}
            dict["host"] = host
            dict["port"] = port
            RedisNodesList.append(dict)
        return RedisNodesList

    def getRedisType(self):
        return self.getConfig("redis_type", "type")

    def getInfogather_db(self):
        return [node for node in self.getAllSection() if node[:16] == "infogather_mysql"]
