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


