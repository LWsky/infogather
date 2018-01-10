#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import socket,fcntl,struct
import time
import psutil
import types
import rediscluster
import sys
import re
from initInformation import *

disk_last = None
net_last = None
jdk_v = check_jkd_version()
print jdk_v

class InfoGather():

    def __init__(self):
        self.hostname = socket.gethostname()
        #print self.hostname
        self.ip = socket.gethostbyname(self.hostname)
    def redis_cluster(self):
        redis_nodes = [{'host': '10.46.185.48', 'port': 7001},
                       {'host': '10.46.185.48', 'port': 7002},
                       {'host': '10.46.185.48', 'port': 7003},
                       {'host': '10.46.185.48', 'port': 7004},
                       {'host': '10.46.185.48', 'port': 7005},
                       {'host': '10.46.185.48', 'port': 7006}
                       ]
        try:
            redisconn = rediscluster.StrictRedisCluster(startup_nodes=redis_nodes,password='jHxG2b9sQiJ3VsoJ')
        except Exception as e:
            print 'redis连接失败，原因', format(e)
            sys.exit(1)
        return redisconn

    def get_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    def get_cpu(self):

        cpu_pipe = os.popen('top -bi -n 2 -d 3').read().split('\n\n\n')[0].split('top - ')[2].split('\n')[2]
        cpu_rb_pipe = os.popen("vmstat 1 2").readlines()
        #print cpu_rb_pipe
        cpu_rb_res = [line.strip("\n").split() for line in cpu_rb_pipe][-1]
        #print cpu_rb_res
        cpu_res = cpu_pipe[8:].split()
        if len(cpu_res[5]) != 3:
            temp1 = cpu_res[5].split(",")
            temp2 = cpu_res[:5]
            temp3 = cpu_res[6:]
            cpu_res = temp2 + temp1 + temp3
        r_cpu = int(cpu_rb_res[0])
        b_cpu = int(cpu_rb_res[1])
        in_cpu = int(cpu_rb_res[-7])
        cs_cpu = int(cpu_rb_res[-6])
        user_cpu = float(cpu_res[0])
        hi_cpu = float(cpu_res[10])
        system_cpu = float(cpu_res[2])
        wa_cpu = float(cpu_res[8])
        si_cpu = float(cpu_res[12])
        idle_cpu = float(cpu_res[6])
        create_time = self.get_time()
        usage_cpu = float(100.0 - idle_cpu)
        load_avg = float(os.getloadavg()[0])
        cpu_usage_data = {
            'host_name':self.hostname,
            'ip':self.ip,
            'r_cpu':r_cpu,
            'b_cpu':b_cpu,
            'in_cpu':in_cpu,
            'cs_cpu':cs_cpu,
            'create_time':create_time,
            'user_cpu':user_cpu,
            'hi_cpu':hi_cpu,
            'system_cpu':system_cpu,
            'wa_cpu':wa_cpu,
            'si_cpu':si_cpu,
            'idle_cpu':idle_cpu,
            'usage_cpu':usage_cpu,
            'load_avg':load_avg
        }

        data = cpu_usage_data
        return data

    # --------------------men--------------------
    def get_mem(self):
        mem_pipe = os.popen("free -m").readlines()
        mem_res = [line.strip("\n").split() for line in mem_pipe]
        mem = mem_res[1]
        swap = mem_res[-1]
        total_mem = int(mem[1])
        used_mem = int(mem[2])
        free_mem = int(mem[3])
        total_swap = int(swap[1])
        used_swap = int(swap[2])
        free_swap = int(swap[3])
        create_time = self.get_time()
        if len(mem) > 5:
            mem_buffcache = int(mem[5])
        else:
            mem_buffcache = int(0)
        mem_usage_data = {
            'host_name': self.hostname,
            'ip': self.ip,
            'create_time': create_time,
            'mem_total':total_mem,
            'mem_used':used_mem,
            'mem_free':free_mem,
            'mem_buffcache':mem_buffcache,
            'swap_total':total_swap,
            'swap_used':used_swap,
            'swap_free':free_swap
        }
        data = mem_usage_data
        return data
    # --------------------men end--------------------
    #--------------------disk--------------------
    def tonum(self,n):
        if str(n).isdigit():
            return int(n)
        return n

    def dist_io_counters(self):
        lines = file("/proc/partitions").readlines()[2:]
        partitions = set([line.split()[-1] for line in lines if not line.strip()[-1].isdigit()])

        def line_to_dict(line):
            major, minor, dev, r_ios, r_merges, r_sec, r_ticks, w_ios, w_merges, w_sec, w_ticks, ios_pgr, tot_ticks, rq_ticks = line.split()
            del line
            d = {k:self.tonum(v) for k,v in locals().items()}
            d['ts'] = time.time()
            return d

        lines = file("/proc/diskstats").readlines()
        stats = [line_to_dict(line) for line in lines]
        stats = {stat["dev"]:stat for stat in stats if stat["dev"] in partitions}
        return stats

    def disk_io_calc(self,last,curr):
        SECTOR_SIZE = 512
        stat = {}

        def diff(field):
            return (curr[field] - last[field]) / (curr["ts"] - last["ts"])

        stat['rrqm_s'] = round(diff('r_merges'),2)
        stat['wrqm_s'] = round(diff('w_merges'),2)
        stat['r_s'] = round(diff('r_ios'),2)
        stat['w_s'] = round(diff('w_ios'),2)
        stat['rkB_s'] = round(diff('r_sec') * SECTOR_SIZE / 1024,2)
        stat['wkB_s'] = round(diff('w_sec') * SECTOR_SIZE / 1024,2)
        stat['avgqu_sz'] = round(diff('rq_ticks') / 1000,2)
        stat['util'] = round(diff('tot_ticks') / 10,2)

        if diff('r_ios') + diff('w_ios') > 0:
            stat['avgrq_sz'] = round((diff('r_sec') + diff('w_sec')) / (diff('r_ios') + diff('w_ios')),2)
            stat['await'] = round((diff('r_ticks') + diff('w_ticks')) / (diff('r_ios') + diff('w_ios')),2)
            stat['svctm'] = round(diff('tot_ticks') / (diff('r_ios') + diff('w_ios')),2)
        else:
            stat['avgrq_sz'] = 0
            stat['await'] = 0
            stat['svctm'] = 0

        return stat


    def get_disk_calc_result(self):
        global disk_last
        curr = self.dist_io_counters()
        if not disk_last:
            disk_last = curr
            return

        stat = {}
        for dev in curr.keys():
            stat[dev] = self.disk_io_calc(disk_last[dev],curr[dev])
        disk_last = curr
        return stat

    def get_disk(self):
        stat = self.get_disk_calc_result()
        if stat:
            for dev in stat.keys():
                stat[dev]["host_name"] = self.hostname
                stat[dev]["ip"] = self.ip
                stat[dev]["Device"] = dev
                stat[dev]["create_time"] = self.get_time()
        data = stat
        #print data
        return data

    # --------------------disk end--------------------
    #--------------------net--------------------
    def net_io_pipe(self):
        def netline_to_dict(line):
            # print line[1:]
            adapter_name, re_bytes, re_packets, re_errs, re_drop, re_fifo, re_frame, re_comperssed, re_multicast, tr_bytes, tr_packets, tr_errs, tr_drop, tr_fifo, tr_colls, tr_carrier, tr_compressed = line.split()
            del line
            d = {k: self.tonum(v) for k, v in locals().items()}

            return d

        net_io_pipe = file("/proc/net/dev").readlines()[2:]
        net_io_info = [netline_to_dict(line) for line in net_io_pipe]
        net_io_info = {name["adapter_name"]: name for name in net_io_info}

        return net_io_info

    def net_io_calc(self,last, curr):
        def diff(field):
            return curr[field] - last[field]

        stat = {}
        stat["re_bytes"] = diff("re_bytes")
        stat["re_packets"] = diff("re_packets")
        stat["re_errors"] = diff("re_errs")
        stat["re_drops"] = diff("re_drop")
        stat["tr_bytes"] = diff("tr_bytes")
        stat["tr_packets"] = diff("tr_packets")
        stat["tr_errors"] = diff("tr_errs")
        stat["tr_drops"] = diff("tr_drop")

        return stat

    def get_net_calc_result(self):
        global net_last

        curr = self.net_io_pipe()
        if not net_last:
            net_last = curr
            return

        stat = {}
        for name in curr.keys():
            stat[name] = self.net_io_calc(net_last[name], curr[name])
        net_last = curr
        return stat

    def get_net(self):
        stat = self.get_net_calc_result()
        if stat:
            for dev in stat.keys():
                stat[dev]["host_name"] = self.hostname
                stat[dev]["ip"] = self.ip
                stat[dev]["adapter_name"] = dev[:-1]
                stat[dev]["create_time"] = self.get_time()
        data = stat
        #print data
        return data

    #--------------------net end--------------------
    # --------------------jvm--------------------
    def get_jvm_gc(self):
        jvm_pipe = os.popen("ps -ef|grep java | grep -v grep").readlines()
        jvm_res = [line.strip().split() for line in jvm_pipe]
        jvm_infos = {}
        def jvm_info_todict(line):
            if jdk_v != 1:
                S0C, S1C, S0U, S1U, EC, EU, OC, OU, PC, PU, YGC, YGCT, FGC, FGCT, GCT = line.split()
            else:
                S0C, S1C, S0U, S1U, EC, EU, OC, OU, MC, MU, PC, PU, YGC, YGCT, FGC, FGCT, GCT = line.split()
            del line
            d = {k:self.tonum(v) for k,v in locals().items()}
            return d

        for i in jvm_res:
            jvm_info = {}
            for j in i:
                if "Dcatalina.home" in j:
                    jvm_info["name_path"] = j
                    jvm_info["pid"] = i[1]
                    jvm_gc_info = os.popen("jstat -gc " + i[1]).readlines()
                    jvm_gc_info = jvm_info_todict(jvm_gc_info[1])
                    jvm_gc_info.pop("self")
                    gc_info = dict(jvm_info,**jvm_gc_info)
                    gc_info["host_name"] = self.hostname
                    gc_info["ip"] = self.ip
                    gc_info["create_time"] = self.get_time()
                    jvm_infos[i[1]] = gc_info
                if "platform.jar" in j:
                    jvm_info["name_path"] = i[-1]
                    jvm_info["pid"] = i[1]
                    jvm_gc_info = os.popen("jstat -gc " + i[1]).readlines()
                    jvm_gc_info = jvm_info_todict(jvm_gc_info[1])
                    jvm_gc_info.pop("self")
                    gc_info = dict(jvm_info, **jvm_gc_info)
                    gc_info["host_name"] = self.hostname
                    gc_info["ip"] = self.ip
                    gc_info["create_time"] = self.get_time()
                    jvm_infos[i[1]] = gc_info
        data = jvm_infos
        return data

    # --------------------jvm end--------------------
    # --------------------redis--------------------
    def get_redis_info(self):
        redisconn = self.redis_cluster()
        redis_info = redisconn.info()
        redis_infos = {}
        def get_dbs(strings):
            r = re.compile(r'db\d')
            return r.findall(strings)
        for key in redis_info.keys():
            info = {}
            db_names = get_dbs(''.join(redis_info[key].keys()))
            info['node'] = key.split(":")[1]
            info['used_memory'] = redis_info[key]['used_memory']
            info['mem_fragmentation_ratio'] = redis_info[key]['mem_fragmentation_ratio']  # 内存碎片率.内存碎片率超过了1.5，那可能是操作系统或Redis实例中内存管理变差的表现
            info['total_commands_processed'] = redis_info[key]['total_commands_processed']  # Redis服务处理命令的总数
            info['used_cpu_sys'] = redis_info[key]['used_cpu_sys']  # redis server的sys cpu使用率
            info['used_cpu_user'] = redis_info[key]['used_cpu_user']  # redis server的user cpu使用率
            db_values = []
            for db in db_names:
                db_values.append(db+':'+redis_info[key][db]['keys'])
            info['keys_num'] = ''.join(db_values)
            info['keyspace_hits'] = redis_info[key]['keyspace_hits']    #key命中数
            info['keyspace_misses'] = redis_info[key]['keyspace_misses']    #key miss数
            info['blocked_clients'] = redis_info[key]['blocked_clients']  # 被阻塞的客户端数
            info['connected_clients'] = redis_info[key]['connected_clients']  # 连接的客户端数
            info['instantaneous_ops_per_sec'] = redis_info[key]['instantaneous_ops_per_sec']  # 每秒执行的命令个数
            info["host_name"] = self.hostname
            info["ip"] = self.ip
            info["create_time"] = self.get_time()
            redis_infos[key] = info
        data = redis_infos
        return data
    # --------------------redis end--------------------

    def main(self):
        data = dict()
        data["cpu"] = self.get_cpu()
        data["mem"] = self.get_mem()
        return data

if __name__ == '__main__':
    info = InfoGather()
    #info.get_disk()
    #a = info.main()
    #print a
    info.get_jvm_gc()
'''
    while True:
        print info.get_cpu()
        print "456"
        time.sleep(1)
        '''
