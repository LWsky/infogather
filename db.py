#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import mysql.connector
import infogather
import time
import datetime

class DB():
    def __init__(self):

        config = {'user': 'root',
                  'password': 'A2017in!!',
                  'host': '10.1.9.199',
                  'port': '3306',
                  'database': 'supervisory_platform',
                  'charset': 'utf8'}
        try:
            self.conn = mysql.connector.connect(**config)
        except mysql.connector.Error as e:
            print "connect fails!{}".format(e)
        self.info = infogather.InfoGather()


    def insert_data(self,data):
        cursor = self.conn.cursor()
        cpu_sql = "INSERT INTO cpu(host_name,ip,r_cpu,b_cpu,in_cpu,cs_cpu,user_cpu,hi_cpu,si_cpu,system_cpu,wa_cpu,idle_cpu,usage_cpu,load_avg,create_time) " \
                  "VALUES (%(host_name)s,%(ip)s,%(r_cpu)s,%(b_cpu)s,%(in_cpu)s,%(cs_cpu)s,%(user_cpu)s,%(hi_cpu)s,%(si_cpu)s,%(system_cpu)s,%(wa_cpu)s,%(idle_cpu)s,%(usage_cpu)s,%(load_avg)s,%(create_time)s)"

        mem_sql = "INSERT INTO mem(host_name,ip,create_time,mem_total,mem_used,mem_free,swap_total,swap_used,swap_free) " \
                  "VALUES (%(host_name)s,%(ip)s,%(create_time)s,%(mem_total)s,%(mem_used)s,%(mem_free)s,%(swap_total)s,%(swap_used)s,%(swap_free)s)"

        disk_sql = "INSERT INTO disk(host_name, ip, create_time, Device, rrqm_s, wrqm_s, r_s, w_s, rkB_s, wkB_s, avgrq_sz, avgqu_sz, await, svctm, util) " \
                   "VALUES (%(host_name)s, %(ip)s, %(create_time)s, %(Device)s, %(rrqm_s)s, %(wrqm_s)s, %(r_s)s, %(w_s)s, %(rkB_s)s, %(wkB_s)s, %(avgrq_sz)s, %(avgqu_sz)s, %(await)s, %(svctm)s, %(util)s)"

        net_sql = "INSERT INTO net(host_name, ip, create_time, adapter_name, re_bytes, re_packets, re_errors, re_drops, tr_bytes, tr_packets, tr_errors, tr_drops) " \
                  "VALUES (%(host_name)s, %(ip)s, %(create_time)s, %(adapter_name)s, %(re_bytes)s, %(re_packets)s, %(re_errors)s, %(re_drops)s, %(tr_bytes)s, %(tr_packets)s, %(tr_errors)s, %(tr_drops)s)"

        jvm_gc_sql = "INSERT INTO jvm_gc (host_name, ip, create_time, PID, name_path, S0C, S1C, S0U, S1U, EC, EU, OC, OU, PC, PU, YGC, YGCT, FGC, FGCT, GCT) " \
                     "VALUES (%(host_name)s, %(ip)s, %(create_time)s, %(PID)s, %(name_path)s, %(S0C)s, %(S1C)s, %(S0U)s, %(S1U)s, %(EC)s, %(EU)s, %(OC)s, %(OU)s, %(PC)s, %(PU)s, %(YGC)s, %(YGCT)s, %(FGC)s, %(FGCT)s, %(GCT)s)"

        all_sql = [cpu_sql,mem_sql,disk_sql,net_sql,jvm_gc_sql]
        try:
            for sql in all_sql:
                if "cpu" in sql:
                    cursor.execute(sql,data["cpu"])
                if "mem" in sql:
                    cursor.execute(sql,data["mem"])
                if "disk" in sql:
                    disk_io_datas = self.info.get_disk()
                    if disk_io_datas:
                        for dev in disk_io_datas.keys():
                            cursor.execute(sql,disk_io_datas[dev])
                if "net" in sql:
                    net_io_datas = self.info.get_net()
                    #print net_io_datas

                    if net_io_datas:
                        for dev in net_io_datas.keys():
                            cursor.execute(sql,net_io_datas[dev])
                if "jvm_gc" in sql:
                    jvm_gc_datas = self.info.get_jvm_gc()
                    if jvm_gc_datas:
                        for pid in jvm_gc_datas.keys():
                            cursor.execute(sql,jvm_gc_datas[pid])
            self.conn.commit()
        except mysql.connector.Error as e:
            print "commit fails!{}".format(e)
        finally:
            cursor.close()
            self.conn.close()

    def insert_all_data(self,interval=2):
        while True:

            data = self.info.main()
            db = DB()
            db.insert_data(data)
            time.sleep(interval)

    def main(self):
        self.insert_all_data()

if __name__ == '__main__':
    db = DB()
    db.main()