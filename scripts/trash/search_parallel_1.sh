
#!/bin/bash
query_dir=query #/home/coast/project/QbE/BUT/PhnRec/PHN_CZ_SPDAT_LCRC_N1500/SWS2013/posteriorgram/query_dev
utt_dir=utt #/home/coast/project/QbE/BUT/PhnRec/PHN_CZ_SPDAT_LCRC_N1500/SWS2013/posteriorgram/utt
ret_dir=ret #/home/coast/project/QbE/BUT/PhnRec/PHN_CZ_SPDAT_LCRC_N1500/SWS2013/ret

function dtw { # 此处定义一个函数，作为一个线程(子进程)
	fn=`echo ${2}|sed 's:\(.*\)\..*:\1:g' `	
  	echo `python dtw.py ${1}/${2} ${3}/${4}` >> ${5}/${fn}.txt
	
}


tmp_fifofile="/tmp/$.fifo"
mkfifo $tmp_fifofile          # 新建一个fifo类型的文件
exec 6<>$tmp_fifofile      # 将fd6指向fifo类型
rm $tmp_fifofile


thread=15 # 此处定义线程数
for ((i=0;i<$thread;i++));do
echo
done >&6 # 事实上就是在fd6中放置了$thread个回车符

feats_query=`python readFeat.py $query_dir`
feats_utt=`python readFeat.py $utt_dir`

for query_file in `ls $query_dir`
do
	feats_query=`python readFeat.py $query_dir`
done

echo $feats_query > tmp
echo ${#feats_query[1]}



for query_file in `ls $query_dir`
do
{
	fn=`echo ${query_file}|sed 's:\(.*\)\..*:\1:g' `
	echo 'searching for '$fn
	st=`date '+%Y-%m-%d %H:%M:%S'`
	echo 'searching for '${fn}':start at '${st} >> ${ret_dir}/log

	for utt_file in `ls $utt_dir`
	do
	read -u6
	{
		dtw $query_dir $query_file $utt_dir $utt_file $ret_dir
		echo >&6
	}&	
	done

	et=`date '+%Y-%m-%d %H:%M:%S'`
	echo 'end at '${et} >> ${ret_dir}/log
}
done


wait # 等待所有的后台子进程结束
exec 6>&- # 关闭df6



