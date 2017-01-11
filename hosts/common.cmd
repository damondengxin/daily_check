cpu核数:grep 'processor' /proc/cpuinfo  |wc -l
cpu负载:uptime | awk '{print $8,$9,$10,$11,$12}'
内存: free  -m |grep '^Mem' |awk '{print $2}'
swap使用情况:free -m | awk '{if(NR==3){print $3}}'
磁盘空间:df -lP | grep -e '^/dev' |awk '{print $1 , $5}'
开机启动:cat /etc/rc.local  |grep -v '^#'|grep -v '^$'|grep -v '^touch'
计划任务:crontab  -l |grep -v '^#'|grep -v '^$'
