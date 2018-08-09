CREATE TABLE `cpu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(100) NOT NULL,
  `ip` varchar(100) NOT NULL,
  `r_cpu` int(11) NOT NULL COMMENT '运行队列',
  `b_cpu` int(11) NOT NULL COMMENT '阻塞的进程',
  `in_cpu` int(11) NOT NULL COMMENT '每秒CPU的中断次数，包括时间中断',
  `cs_cpu` int(11) NOT NULL COMMENT '每秒上下文切换次数',
  `user_cpu` float(11,2) NOT NULL,
  `hi_cpu` float(11,2) NOT NULL,
  `si_cpu` float(11,2) NOT NULL,
  `system_cpu` float(11,2) NOT NULL,
  `wa_cpu` float(11,2) NOT NULL,
  `idle_cpu` float(11,2) NOT NULL,
  `usage_cpu` float(11,2) NOT NULL,
  `load_avg` float(11,2) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `disk` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(100) NOT NULL,
  `ip` varchar(20) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Device` varchar(20) NOT NULL,
  `rrqm_s` float(20,2) NOT NULL COMMENT '每秒进行 merge 的读操作数目',
  `wrqm_s` float(20,2) NOT NULL COMMENT '每秒进行 merge 的写操作数目',
  `r_s` float(20,2) NOT NULL COMMENT ' 每秒完成的读 I/O 设备次数',
  `w_s` float(20,2) NOT NULL COMMENT '每秒完成的写 I/O 设备次数',
  `rkB_s` float(20,2) NOT NULL COMMENT '每秒读K字节数。是 rsect/s 的一半，因为每扇区大小为512字节',
  `wkB_s` float(20,2) NOT NULL COMMENT '每秒写K字节数。是 wsect/s 的一半',
  `avgrq_sz` float(20,2) NOT NULL COMMENT '平均每次设备I/O操作的数据大小 (扇区)。delta(rsect+wsect)/delta(rio+wio)',
  `avgqu_sz` float(20,2) NOT NULL COMMENT '平均I/O队列长度。即 delta(aveq)/s/1000 (因为aveq的单位为毫秒)',
  `await` float(20,2) NOT NULL COMMENT '平均每次设备I/O操作的等待时间 (毫秒)。即 delta(ruse+wuse)/delta(rio+wio)',
  `svctm` float(20,2) NOT NULL COMMENT '平均每次设备I/O操作的服务时间 (毫秒)。即 delta(use)/delta(rio+wio)',
  `util` float(20,2) NOT NULL COMMENT '一秒中有百分之多少的时间用于 I/O 操作，或者说一秒中有多少时间 I/O 队列是非空的',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `jvm_gc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(100) NOT NULL,
  `ip` varchar(100) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `PID` int(11) NOT NULL,
  `name_path` varchar(50) NOT NULL,
  `S0C` int(11) NOT NULL,
  `S1C` int(11) NOT NULL,
  `S0U` int(11) NOT NULL,
  `S1U` int(11) NOT NULL,
  `EC` int(11) NOT NULL,
  `EU` int(11) NOT NULL,
  `OC` int(11) NOT NULL,
  `OU` int(11) NOT NULL,
  `PC` int(11) NOT NULL,
  `PU` int(11) NOT NULL,
  `YGC` int(11) NOT NULL,
  `YGCT` int(11) NOT NULL,
  `FGC` int(11) NOT NULL,
  `FGCT` int(11) NOT NULL,
  `GCT` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `mem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(100) NOT NULL,
  `ip` varchar(100) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mem_total` int(11) NOT NULL,
  `mem_used` float(11,2) NOT NULL,
  `mem_free` int(11) NOT NULL,
  `mem_buffcache` int(11) NOT NULL,
  `swap_total` int(11) NOT NULL,
  `swap_used` int(11) NOT NULL,
  `swap_free` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `net` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(100) NOT NULL,
  `ip` varchar(100) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `adapter_name` varchar(50) NOT NULL,
  `re_bytes` int(11) NOT NULL,
  `re_packets` int(11) NOT NULL,
  `re_errors` int(11) NOT NULL,
  `re_drops` int(11) NOT NULL,
  `tr_bytes` int(11) NOT NULL,
  `tr_packets` int(11) NOT NULL,
  `tr_errors` int(11) NOT NULL,
  `tr_drops` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `redis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(50) NOT NULL,
  `ip` varchar(20) NOT NULL,
  `node` varchar(50) NOT NULL,
  `used_memory` int(11) NOT NULL,
  `mem_fragmentation_ratio` float(11,2) NOT NULL COMMENT '内存碎片率.内存碎片率超过了1.5，那可能是操作系统或Redis实例中内存管理变差的表现',
  `total_commands_processed` int(11) NOT NULL COMMENT 'Redis服务处理命令的总数',
  `used_cpu_sys` float(11,2) NOT NULL,
  `used_cpu_user` float(11,2) NOT NULL,
  `blocked_clients` int(11) NOT NULL COMMENT '被阻塞的客户端数',
  `connected_clients` int(11) NOT NULL COMMENT '连接的客户端数',
  `instantaneous_ops_per_sec` int(11) NOT NULL COMMENT '每秒执行的命令个数',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `mysql` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(50) NOT NULL,
  `ip` varchar(20) NOT NULL,
  `masterOrslave` varchar(50) NOT NULL,
  `InnnoDB_QPS` int(11) NOT NULL,
  `MyISAM_QPS` int(11) NOT NULL,
  `TPS` int(11) NOT NULL,
  `Threads_cached` int(11) NOT NULL COMMENT '代表当前此时此刻线程缓存中有多少空闲线程',
  `Threads_running` int(11) NOT NULL COMMENT '代表当前激活的（非睡眠状态）线程数',
  `Threads_connected` int(11) NOT NULL COMMENT '代表当前已建立连接的数量，因为一个连接就需要一个线程，所以也可以看成当前被使用的线程数',
  `thread_cache_hitrate` float(11,2) NOT NULL COMMENT '线程缓存命中率',
  `key_buffer_read_hits` float(11,2) NOT NULL COMMENT 'key buffer read 命中率',
  `key_buffer_write_hits` float(11,2) NOT NULL COMMENT 'key buffer write 命中率',
  `query_cache_hits` float(11,2) NOT NULL COMMENT 'query cache命中率',
  `max_connections` int(11) NOT NULL COMMENT '最大连接数',
  `Max_used_connections` int(11) NOT NULL COMMENT '最大使用连接数',
  `innodb_buffer_read_hit_ratio` float(11,2) NOT NULL COMMENT 'innodb 缓冲池的读命中率',
  `Innodb_buffer_usage` float(11,2) NOT NULL COMMENT 'Innodb缓冲池的利用率',
  `innodb_buffer_pool_hit_ratio` float(11,2) NOT NULL COMMENT '缓冲池命中率',
  `Created_tmp_tables` int(11) NOT NULL COMMENT '服务器执行语句时自动创建的内存中的临时表的数量',
  `Created_tmp_disk_tables` int(11) NOT NULL COMMENT '服务器执行语句时在硬盘上自动创建的临时表的数量',
  `Handler_read_prev` int(11) NOT NULL COMMENT '此选项表明在进行索引扫描时， 按照索引倒序从数据文件里取数据的次数， 一般就是ORDER BY... DESC',
  `Handler_read_rnd_next` int(11) NOT NULL COMMENT '使用数据文件进行扫描的次数，该值越大证明有大量的全表扫描，或者合理地创建索引,没有很好地利用已经建立好的索引',
  `Handler_read_first` int(11) NOT NULL COMMENT '使用索引扫描的次数，该值大小说不清系统性能是好是坏',
  `Handler_read_key` int(11) NOT NULL COMMENT '通过key进行查询的次数，该值越大证明系统性能越好',
  `Handler_read_next` int(11) NOT NULL COMMENT '使用索引进行排序的次数',
  `Handler_read_rnd` int(11) NOT NULL COMMENT '该值越大证明系统中有大量的没有使用索引进行排序的操作，或者join时没有使用到index',
  `Handler_read_last` int(11) NOT NULL COMMENT 'The number of requests to read the last key in an index. With ORDER BY, the server will issue a first-key request followed by several next-key requests, whereas with ORDER BY DESC, the server will issue a last-key request followed by several previous-key requests. This variable was added in MySQL 5.6.1.',
  `Slow_queries` int(11) NOT NULL COMMENT '慢查询总数',
  `long_query_time` int(11) NOT NULL COMMENT '最长查询时间',
  `Table_locks_immediate` int(11) NOT NULL COMMENT '可以立即授予对表锁请求的次数',
  `Table_locks_waited` int(11) NOT NULL COMMENT '不能立即授予一个表锁请求的次数，需要等待。如果这是高的，并且您有性能问题，您应该首先优化您的查询，然后可以拆分您的表或表或使用复制。',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `server_ip` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(100) NOT NULL,
  `ip` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;