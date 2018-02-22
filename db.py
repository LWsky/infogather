#!/usr/bin/python
# -*- coding:utf-8 -*-

import inspect
import mysql.connector
import infogather
import time
import threading
import initInformation
import my_config


class DB():
    def __init__(self):

        self.info = infogather.InfoGather()

    def connect_mysql(self):
        try:
            config = {'user': my_config.getConfig("mysql","user"),
                      'password': my_config.getConfig("mysql","password"),
                      'host': my_config.getConfig("mysql","host"),
                      'port': my_config.getConfig("mysql","port"),
                      'database': my_config.getConfig("mysql","database"),
                      'charset': my_config.getConfig("mysql","charset")}
            conn = mysql.connector.connect(**config)
            return conn
        except mysql.connector.Error as e:
            print "connect fails!{}".format(e)

    def insert_cpu(self,interval=2):
        #cursor = self.conn.cursor()
        while True:
            cpu_sql = "INSERT INTO cpu(host_name,ip,r_cpu,b_cpu,in_cpu,cs_cpu,user_cpu,hi_cpu,si_cpu,system_cpu,wa_cpu,idle_cpu,usage_cpu,load_avg,create_time) " \
                      "VALUES (%(host_name)s,%(ip)s,%(r_cpu)s,%(b_cpu)s,%(in_cpu)s,%(cs_cpu)s,%(user_cpu)s,%(hi_cpu)s,%(si_cpu)s,%(system_cpu)s,%(wa_cpu)s,%(idle_cpu)s,%(usage_cpu)s,%(load_avg)s,%(create_time)s)"
            conn = self.connect_mysql()
            cursor = conn.cursor()
            try:
                data = self.info.get_cpu()
                cursor.execute(cpu_sql,data)
                conn.commit()
            except mysql.connector.Error as e:
                print "insert_cpu commit fails!{}".format(e)
            finally:
                cursor.close()
                conn.close()
            time.sleep(interval)


    def insert_men(self,interval=2):
        #cursor = self.conn.cursor()
        while True:
            mem_sql = "INSERT INTO mem(host_name,ip,create_time,mem_total,mem_used,mem_free,mem_buffcache,swap_total,swap_used,swap_free) " \
                      "VALUES (%(host_name)s,%(ip)s,%(create_time)s,%(mem_total)s,%(mem_used)s,%(mem_free)s,%(mem_buffcache)s,%(swap_total)s,%(swap_used)s,%(swap_free)s)"
            conn = self.connect_mysql()
            cursor = conn.cursor()
            try:
                data = self.info.get_mem()
                cursor.execute(mem_sql,data)
                conn.commit()
            except mysql.connector.Error as e:
                print "insert_mem commit fails!{}".format(e)
            finally:
                cursor.close()
                conn.close()
            time.sleep(interval)


    def insert_disk(self,interval=2):
        #cursor = self.conn.cursor()
        while True:
            disk_sql = "INSERT INTO disk(host_name, ip, create_time, Device, rrqm_s, wrqm_s, r_s, w_s, rkB_s, wkB_s, avgrq_sz, avgqu_sz, await, svctm, util) " \
                       "VALUES (%(host_name)s, %(ip)s, %(create_time)s, %(Device)s, %(rrqm_s)s, %(wrqm_s)s, %(r_s)s, %(w_s)s, %(rkB_s)s, %(wkB_s)s, %(avgrq_sz)s, %(avgqu_sz)s, %(await)s, %(svctm)s, %(util)s)"
            conn = self.connect_mysql()
            cursor = conn.cursor()
            data = self.info.get_disk()
            if data:
                try:
                    for dev in data.keys():
                        cursor.execute(disk_sql,data[dev])
                    conn.commit()
                except mysql.connector.Error as e:
                    print "insert_disk commit fails!{}".format(e)
                finally:
                    cursor.close()
                    conn.close()
            time.sleep(interval)


    def insert_net(self,interval=2):
        #cursor = self.conn.cursor()
        while True:
            net_sql = "INSERT INTO net(host_name, ip, create_time, adapter_name, re_bytes, re_packets, re_errors, re_drops, tr_bytes, tr_packets, tr_errors, tr_drops) " \
                      "VALUES (%(host_name)s, %(ip)s, %(create_time)s, %(adapter_name)s, %(re_bytes)s, %(re_packets)s, %(re_errors)s, %(re_drops)s, %(tr_bytes)s, %(tr_packets)s, %(tr_errors)s, %(tr_drops)s)"
            conn = self.connect_mysql()
            cursor = conn.cursor()
            data = self.info.get_net()
            if data:
                try:
                    for dev in data.keys():
                        cursor.execute(net_sql,data[dev])
                    conn.commit()
                except mysql.connector.Error as e:
                    print "insert_net commit fails!{}".format(e)
                finally:
                    cursor.close()
                    conn.close()
            time.sleep(interval)

    def insert_jvm_gc(self,interval=2):
        #cursor = self.conn.cursor()
        while True:
            jvm_gc_sql = "INSERT INTO jvm_gc (host_name, ip, create_time, PID, name_path, S0C, S1C, S0U, S1U, EC, EU, OC, OU, PC, PU, YGC, YGCT, FGC, FGCT, GCT) " \
                         "VALUES (%(host_name)s, %(ip)s, %(create_time)s, %(pid)s, %(name_path)s, %(S0C)s, %(S1C)s, %(S0U)s, %(S1U)s, %(EC)s, %(EU)s, %(OC)s, %(OU)s, %(PC)s, %(PU)s, %(YGC)s, %(YGCT)s, %(FGC)s, %(FGCT)s, %(GCT)s)"
            conn = self.connect_mysql()
            cursor = conn.cursor()
            data = self.info.get_jvm_gc()
            if data:
                try:
                    for pid in data.keys():
                        cursor.execute(jvm_gc_sql,data[pid])
                    conn.commit()
                except mysql.connector.Error as e:
                    print "insert_jvm_gc commit fails!{}".format(e)
                finally:
                    cursor.close()
                    conn.close()
            time.sleep(interval)

    def insert_redis_info(self, interval=2):
        while True:
            redis_info_sql = "INSERT INTO redis (host_name, ip, node, used_memory, mem_fragmentation_ratio, total_commands_processed, used_cpu_sys, used_cpu_user, blocked_clients, connected_clients, instantaneous_ops_per_sec, create_time) " \
                         "VALUES (%(host_name)s, %(ip)s, %(node)s, %(used_memory)s, %(mem_fragmentation_ratio)s, %(total_commands_processed)s, %(used_cpu_sys)s, %(used_cpu_user)s, %(blocked_clients)s, %(connected_clients)s, %(instantaneous_ops_per_sec)s, %(create_time)s)"
            conn = self.connect_mysql()
            cursor = conn.cursor()
            data = self.info.get_redis_info()
            if data:
                try:
                    for node in data.keys():
                        cursor.execute(redis_info_sql, data[node])
                    conn.commit()
                except mysql.connector.Error as e:
                    print "insert_jvm_gc commit fails!{}".format(e)
                finally:
                    cursor.close()
                    conn.close()
            time.sleep(interval)

    def all_func(self):
        all_data = dict()
        for func in inspect.getmembers(self,predicate=inspect.ismethod):
            if func[0][:6] == 'insert':
                all_data[func[0]] = func[1]
        services_status = initInformation.check_services()
        if services_status['redis'] == 0:
            del all_data['insert_redis_info']
        all_func_data = all_data
        return all_func_data



if __name__ == '__main__':
    db = DB()
    all_insert_func = db.all_func()
    threads = []
    for func in all_insert_func.keys():
        t = threading.Thread(target=all_insert_func[func])
        t.setDaemon(True)
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()