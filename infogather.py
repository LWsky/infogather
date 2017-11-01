#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import socket,fcntl,struct
import time
import psutil

last = None

class InfoGather():

    def __init__(self):
        self.hostname = socket.gethostname()
        #print self.hostname
        self.ip = socket.gethostbyname(self.hostname)

    def get_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    def get_cpu(self):
        cpu_pipe = os.popen("top -bi -n 2 -d 0.02").readlines()[2]
        cpu_rb_pipe = os.popen("vmstat").readlines()
        cpu_rb_res = [line.strip("\n").split() for line in cpu_rb_pipe][2]
        #print cpu_rb_res
        cpu_res = cpu_pipe.split()
        r_cpu = int(cpu_rb_res[0])
        b_cpu = int(cpu_rb_res[1])
        in_cpu = int(cpu_rb_res[-7])
        cs_cpu = int(cpu_rb_res[-6])
        user_cpu = float(cpu_res[1])
        hi_cpu = float(cpu_res[11])
        system_cpu = float(cpu_res[3])
        wa_cpu = float(cpu_res[9])
        si_cpu = float(cpu_res[13])
        idle_cpu = float(cpu_res[7])
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

    def get_mem(self):
        mem_pipe = os.popen("free -m").readlines()
        mem_res = [line.strip("\n").split() for line in mem_pipe]
        mem = mem_res[1]
        swap = mem_res[2]
        total_mem = int(mem[1])
        used_mem = int(mem[2])
        free_mem = int(mem[3])
        total_swap = int(swap[1])
        used_swap = int(swap[2])
        free_swap = int(swap[3])
        create_time = self.get_time()
        mem_usage_data = {
            'host_name': self.hostname,
            'ip': self.ip,
            'create_time': create_time,
            'mem_total':total_mem,
            'mem_used':used_mem,
            'mem_free':free_mem,
            'swap_total':total_swap,
            'swap_used':used_swap,
            'swap_free':free_swap
        }
        data = mem_usage_data
        return data

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
        global last
        curr = self.dist_io_counters()
        if not last:
            last = curr
            return

        stat = {}
        for dev in curr.keys():
            stat[dev] = self.disk_io_calc(last[dev],curr[dev])
        last = curr
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
    while True:
        info.get_disk()
        time.sleep(1)
