#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import socket,fcntl,struct
import time
#import psutil
#import types
import rediscluster
import redis
import sys
import re
from my_config import MyConfig
import db

disk_last = None
net_last = None


class InfoGather():


    def __init__(self):
        self.hostname = socket.gethostname()
        #self.ip = socket.gethostbyname(self.hostname)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'eth0'[:15]))[20:24])
        self.conf = MyConfig()
    def redis_cluster(self):
        redis_nodes = self.conf.getRedisNodes()
        password = self.conf.getConfig("redisCluster","password")
        try:
            redisconn = rediscluster.StrictRedisCluster(startup_nodes=redis_nodes,password=password)
        except Exception as e:
            print 'redis连接失败，原因', format(e)
            sys.exit(1)
        return redisconn

    def redis_conn(self):
        pool = redis.ConnectionPool(host=self.conf.getConfig("redis", "host"), port=self.conf.getConfig("redis", "port"),
                                    password=self.conf.getConfig("redis", "password"), decode_responses=True)
        try:
            redisconn = redis.Redis(connection_pool=pool)
        except Exception as e:
            print 'redis连接失败，原因', format(e)
            sys.exit(1)
        return redisconn

    def get_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    def get_cpu(self):
        cpu_rb_pipe = os.popen("vmstat 1 2").readlines()
        cpu_rb_res = [line.strip("\n").split() for line in cpu_rb_pipe][-1]
        change_sys = os.popen('top -bi -n 2 -d 3').read().split('\n\n\n')
        if len(change_sys) != 2:
            cpu_pipe = os.popen('top -bi -n 2 -d 3').read().split('\n\n\n')[0].split('top - ')[2].split('\n')[2]
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
        else:
            cpu_pipe = os.popen('top -bi -n 2 -d 3').read().split('\n\n\n')[1].split('\n')[2]
            cpu_res = cpu_pipe[8:].split(',')
            cpu_res = [i.strip()[:-3] for i in cpu_res]
            r_cpu = int(cpu_rb_res[0])
            b_cpu = int(cpu_rb_res[1])
            in_cpu = int(cpu_rb_res[-7])
            cs_cpu = int(cpu_rb_res[-6])
            user_cpu = float(cpu_res[0])
            hi_cpu = float(cpu_res[5])
            system_cpu = float(cpu_res[1])
            wa_cpu = float(cpu_res[4])
            si_cpu = float(cpu_res[6])
            idle_cpu = float(cpu_res[3])
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
    # --------------------men--------------------
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
    # --------------------disk end--------------------
    #--------------------net--------------------

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

    def get_jvm_gc(self,version):
        jvm_pipe = os.popen("ps -ef|grep java | grep -v grep").readlines()
        jvm_res = [line.strip().split() for line in jvm_pipe]
        jvm_infos = {}
        def jvm_info_todict(line):
            if version != 1:
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
                    if version != 1:
                        gc_info["MC"] = ''
                        gc_info["MU"] = ''
                    jvm_infos[i[1]] = gc_info
        data = jvm_infos
        return data
    #--------------------net end--------------------
    # --------------------jvm--------------------

    # --------------------jvm end--------------------
    # --------------------redis--------------------
    def get_redis_info(self):
        redis_infos = {}
        if self.conf.getRedisType() == 1:
            redisconn = self.redis_cluster()
            redis_info = redisconn.info()
            def get_dbs(strings):
                r = re.compile(r'db\d')
                return r.findall(strings)
            for key in redis_info.keys():
                info = {}
                db_names = get_dbs(''.join(redis_info[key].keys()))
                info['node'] = key.split(":")[1]
                info['used_memory'] = redis_info['used_memory']
                info['mem_fragmentation_ratio'] = redis_info['mem_fragmentation_ratio']  # 内存碎片率.内存碎片率超过了1.5，那可能是操作系统或Redis实例中内存管理变差的表现
                info['total_commands_processed'] = redis_info['total_commands_processed']  # Redis服务处理命令的总数
                info['used_cpu_sys'] = redis_info['used_cpu_sys']  # redis server的sys cpu使用率
                info['used_cpu_user'] = redis_info['used_cpu_user']  # redis server的user cpu使用率
                db_values = []
                for db in db_names:
                    db_values.append(db+':'+str(redis_info[key][db]['keys']))
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
            else:
                redisconn = self.redis_conn()
                redis_info = redisconn.info()
                info = {}
                info['node'] = "单节点"
                #info['node'] = key.split(":")[1]
                info['used_memory'] = redis_info['used_memory']
                info['mem_fragmentation_ratio'] = redis_info['mem_fragmentation_ratio']  # 内存碎片率.内存碎片率超过了1.5，那可能是操作系统或Redis实例中内存管理变差的表现
                info['total_commands_processed'] = redis_info['total_commands_processed']  # Redis服务处理命令的总数
                info['used_cpu_sys'] = redis_info['used_cpu_sys']  # redis server的sys cpu使用率
                info['used_cpu_user'] = redis_info['used_cpu_user']  # redis server的user cpu使用率
                #db_values = []
                #info['keys_num'] = ''
                info['keyspace_hits'] = redis_info['keyspace_hits']  # key命中数
                info['keyspace_misses'] = redis_info['keyspace_misses']  # key miss数
                info['blocked_clients'] = redis_info['blocked_clients']  # 被阻塞的客户端数
                info['connected_clients'] = redis_info['connected_clients']  # 连接的客户端数
                info['instantaneous_ops_per_sec'] = redis_info['instantaneous_ops_per_sec']  # 每秒执行的命令个数
                info["host_name"] = self.hostname
                info["ip"] = self.ip
                info["create_time"] = self.get_time()
                redis_infos[1] = info
        data = redis_infos
        print data
        return data
    # --------------------redis end--------------------

    # --------------------mysql--------------------
    def get_mysql_info(self,dbnode):
        s = time.time()
        mysql_infos = {}
        mydb = db.DB()
        #判断主从
        if "slave" in dbnode:
            mysql_infos["masterOrslave"] = dbnode[17:]
        else:
            mysql_infos["masterOrslave"] = "master"
        #QPS计算(每秒查询数)
        questions = mydb.query_date(dbnode,"show GLOBAL status like 'Questions'")["Questions"]
        uptime_myisam = mydb.query_date(dbnode,"show global status like 'Uptime'")["Uptime"]
        MyISAM_QPS = round(int(questions)/float(uptime_myisam),2)    #针对MyISAM 引擎为主的DB
        mysql_infos["MyISAM_QPS"] = MyISAM_QPS
        com_update = mydb.query_date(dbnode,"show global status like 'Com_update'")["Com_update"]  #执行update操作的次数
        com_insert = mydb.query_date(dbnode,"show global status like 'Com_insert'")["Com_insert"]  #执行insert操作的次数
        com_select = mydb.query_date(dbnode,"show global status like 'Com_select'")["Com_select"]  #执行select操作的次数
        com_delete = mydb.query_date(dbnode,"show global status like 'Com_delete'")["Com_delete"]  #执行delete操作的次数
        uptime_innodb = mydb.query_date(dbnode,"show global status like 'Uptime'")["Uptime"]
        InnoDB_QPS = round((int(com_update)+int(com_insert)+int(com_delete)+int(com_select))/float(uptime_innodb),2)
        mysql_infos["InnnoDB_QPS"] = InnoDB_QPS
        #TPS计算(每秒事务数)
        com_commit = mydb.query_date(dbnode,"show global status like 'Com_commit'")["Com_commit"]
        com_rollback = mydb.query_date(dbnode,"show global status like 'Com_rollback'")["Com_rollback"]
        uptime_tps = mydb.query_date(dbnode,"show global status like 'Uptime'")["Uptime"]
        TPS = round((int(com_commit) + int(com_rollback)) / float(uptime_tps),2)
        mysql_infos["TPS"] = TPS
        #线程连接数和命中率
        mydbThreads = mydb.query_date(dbnode,"show global status like 'Threads_%'")
        #| Threads_cached | 480 | // 代表当前此时此刻线程缓存中有多少空闲线程
        #| Threads_connected | 153 | // 代表当前已建立连接的数量，因为一个连接就需要一个线程，所以也可以看成当前被使用的线程数
        #| Threads_created | 20344 | // 代表从最近一次服务启动，已创建线程的数量
        #| Threads_running | 2 | // 代表当前激活的（非睡眠状态）线程数
        connections = mydb.query_date(dbnode,"show global status like 'Connections'")["Connections"]
        thread_cache_hitrate = round(1-int(mydbThreads["Threads_cached"])/float(connections),5) #线程缓存命中率
        mysql_infos["Threads_cached"] = mydbThreads["Threads_cached"]
        mysql_infos["Threads_running"] = mydbThreads["Threads_running"]
        mysql_infos["Threads_connected"] = mydbThreads["Threads_connected"]
        mysql_infos["thread_cache_hitrate"] = thread_cache_hitrate
        #key buffer 命中率
        key = mydb.query_date(dbnode,"show status like 'key%'")
        key_buffer_read_hits = round(1 - int(key["Key_reads"]) / float(key["Key_read_requests"]),2)
        if int(key["Key_write_requests"]) != 0:
            key_buffer_write_hits = round(1 - int(key["Key_writes"]) / float(key["Key_write_requests"]),2)
        else:
            key_buffer_write_hits = 0.0
        mysql_infos["key_buffer_read_hits"] = key_buffer_read_hits
        mysql_infos["key_buffer_write_hits"] = key_buffer_write_hits
        # query cache命中率
        qcache = mydb.query_date(dbnode,"show status like 'Qcache%'")
        query_cache_hits = round(int(qcache["Qcache_hits"]) / (float(qcache["Qcache_hits"]) + float(com_select)),5)
        mysql_infos["query_cache_hits"] = query_cache_hits
        #最大连接数
        max_connections = mydb.query_date(dbnode,"show variables like 'max_connections'")["max_connections"]
        max_used_connections = mydb.query_date(dbnode,"show global status like 'Max_used_connections'")["Max_used_connections"]
        mysql_infos["max_connections"] = max_connections
        mysql_infos["Max_used_connections"] = max_used_connections
        #Innodb缓存
        innodb_buffer = mydb.query_date(dbnode,"show global status like 'innodb_buffer_pool%'")
        #Innodb_buffer_pool_read_ahead:后端预读线程读取到innodb buffer pool的页的数目。单位是page。
        #Innodb_buffer_pool_read_ahead_evicted:预读的页数，但是没有被读取就从缓冲池中被替换的页的数量，一般用来判断预读的效率。
        #innodb_buffer_pool_reads: 平均每秒从物理磁盘读取页的次数
        #innodb_buffer_pool_read_requests: 平均每秒从innodb缓冲池的读次数（逻辑读请求数）
        #innodb_buffer_pool_write_requests: 平均每秒向innodb缓冲池的写次数
        #innodb_buffer_pool_pages_dirty: 平均每秒innodb缓存池中脏页的数目
        #innodb_buffer_pool_pages_flushed: 平均每秒innodb缓存池中刷新页请求的数目
        # innodb 缓冲池的读命中率
        innodb_buffer_read_hit_ratio = round(( 1 - int(innodb_buffer["Innodb_buffer_pool_reads"])/float(innodb_buffer["Innodb_buffer_pool_read_requests"])) * 100,2)
        #Innodb缓冲池的利用率
        Innodb_buffer_usage = round((1 - int(innodb_buffer["Innodb_buffer_pool_pages_free"]) / float(innodb_buffer["Innodb_buffer_pool_pages_total"])) * 10,2)
        #缓冲池命中率
        innodb_buffer_pool_hit_ratio = round((int(innodb_buffer["Innodb_buffer_pool_read_requests"])) / float(int(innodb_buffer["Innodb_buffer_pool_read_requests"]) + int(innodb_buffer["Innodb_buffer_pool_read_ahead"]) + int(innodb_buffer["Innodb_buffer_pool_reads"])),5)
        mysql_infos["innodb_buffer_read_hit_ratio"] = innodb_buffer_read_hit_ratio
        mysql_infos["Innodb_buffer_usage"] = Innodb_buffer_usage
        mysql_infos["innodb_buffer_pool_hit_ratio"] = innodb_buffer_pool_hit_ratio
        #临时表使用情况
        created_tmp = mydb.query_date(dbnode,"show global status like 'Created_tmp%'")
        #Created_tmp_disk_tables: 服务器执行语句时在硬盘上自动创建的临时表的数量
        #Created_tmp_tables: 服务器执行语句时自动创建的内存中的临时表的数量
        #Created_tmp_disk_tables / Created_tmp_tables比值最好不要超过10%，如果Created_tmp_tables值比较大,可能是排序句子过多或者连接句子不够优化
        mysql_infos["Created_tmp_disk_tables"] = created_tmp["Created_tmp_disk_tables"]
        mysql_infos["Created_tmp_tables"] = created_tmp["Created_tmp_tables"]
        #表扫描情况判断
        handler_read = mydb.query_date(dbnode,"show global status like 'Handler_read%'")
        #Handler_read_first ：使用索引扫描的次数，该值大小说不清系统性能是好是坏
        #Handler_read_key ：通过key进行查询的次数，该值越大证明系统性能越好
        #Handler_read_next ：使用索引进行排序的次数
        #Handler_read_prev ：此选项表明在进行索引扫描时， 按照索引倒序从数据文件里取数据的次数， 一般就是ORDER BY... DESC
        #Handler_read_rnd ：该值越大证明系统中有大量的没有使用索引进行排序的操作，或者join时没有使用到index
        #Handler_read_rnd_next ：使用数据文件进行扫描的次数，该值越大证明有大量的全表扫描，或者合理地创建索引,没有很好地利用已经建立好的索引
        mysql_infos["Handler_read_first"] = handler_read["Handler_read_first"]
        mysql_infos["Handler_read_key"] = handler_read["Handler_read_key"]
        mysql_infos["Handler_read_last"] = handler_read["Handler_read_last"]
        mysql_infos["Handler_read_next"] = handler_read["Handler_read_next"]
        mysql_infos["Handler_read_prev"] = handler_read["Handler_read_prev"]
        mysql_infos["Handler_read_rnd"] = handler_read["Handler_read_rnd"]
        mysql_infos["Handler_read_rnd_next"] = handler_read["Handler_read_rnd_next"]
        #慢查询
        slow_queries = mydb.query_date(dbnode,"show global status like 'Slow_queries'")["Slow_queries"]
        long_query_time = mydb.query_date(dbnode,"show variables like 'long_query_time'")["long_query_time"]
        mysql_infos["Slow_queries"] = slow_queries
        mysql_infos["long_query_time"] = long_query_time
        e = time.time()
        #表锁
        table_lock = mydb.query_date(dbnode,"show global status like 'table_lock%'")
        # Table_locks_immediate :可以立即授予对表锁请求的次数。
        #Table_locks_waited:不能立即授予一个表锁请求的次数，需要等待。如果这是高的，并且您有性能问题，您应该首先优化您的查询，然后可以拆分您的表或表或使用复制。
        #这两个值的比值： Table_locks_waited / Table_locks_immediate趋向于0，如果值比较大则表示系统的锁阻塞情况比较严重
        mysql_infos["Table_locks_immediate"] = table_lock["Table_locks_immediate"]
        mysql_infos["Table_locks_waited"] = table_lock["Table_locks_waited"]

        mysql_infos["host_name"] = ""
        mysql_infos["ip"] = self.conf.getConfig(dbnode,"host")
        mysql_infos["create_time"] = self.get_time()
        data = mysql_infos
        return data
    # --------------------mysql end--------------------

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
    #info.get_jvm_gc(1)
    conf = MyConfig()
    print conf.getInfogather_db()
    for node in conf.getInfogather_db():
        print info.get_mysql_info(dbnode=node)

'''
    while True:
        print info.get_cpu()
        print "456"
        time.sleep(1)
        '''
