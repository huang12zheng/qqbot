# dir="/home/ubuntu/qqbot_k8s/"
# error: kex qqbot-57658f5d66-9ldpr    -- "/bin/bash  /app/liveness-probe.sh"
# kex qqbot-57658f5d66-9ldpr    -- /bin/bash  /app/liveness-probe.sh
dir="/app/"
path="$dir""cqhttp/logs/"`date +"%Y-%m-%d"`.log

tailContext=`tail -10 $path` # 最后一行可能不是FATAL
flag='\[FATAL\]'
# flag='\[INFO\]'
# flag='a'

# exist=`echo "$tailContext" | grep $flag`
echo "$tailContext" | grep $flag
EXCODE=$?
echo $EXCODE
# 定时重启, 因为 pod是 60检测一次
if [ `date +%k` -eq 0 -a `date +"%_M"` -lt 4 ] # 找到”失败“,要退出
then
    # echo "O.K" 
    exit 1
fi

# if [ "$EXCODE" == "0" ] # EXCODE is no num
if [ "$EXCODE" -eq "0" ] # 找到”失败“,要退出
then
    # echo "O.K" 
    exit 1
fi