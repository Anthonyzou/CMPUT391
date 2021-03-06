#!/bin/sh
echo '\n\n'
echo '	generate test data locally : 		1'
echo '	generate data remotely : 		2 for development only'
echo '	query locally : 			3'
echo '	query remotely : 			4 for development only'
echo '	status :				5'
echo '	ssh into instance 1 :			6'
echo '	make zip :				7'
echo '	generate 16TB locally :			8'
echo '	setup remote machine :			9'
echo '\n\n'

generate(){
	echo '		ENETER DAYS to generate! 1000000 entries are made per day'
	read amount
	echo '		ENTER SEED or leave blank for default seed THIS WILL CLEAR THE SYSTEM'
	read seed 
	echo '		ENTER FILENAME for output'
	read file
	if [ -n "$seed" ]; then
		nohup python -W ignore generate.py $amount $seed > $file &
	else
		nohup python -W ignore generate.py $amount > $file &
	fi
	echo "output goes to $file"
}
generate_big(){
	nohup python -W ignore generate.py 100 > generation_data.txt &
	echo 'data goes to generation_data.txt'
}
remote_generate(){
	echo
	echo 'default group3@199.116.235.57'
	scp  -i NebulaLaunchKey.pem cdr_table.sql group3@199.116.235.57:/home/group3
	scp -i NebulaLaunchKey.pem tablestuffs.txt group3@199.116.235.57:/home/group3
	cat generate.py | ssh -i NebulaLaunchKey.pem group3@199.116.235.57 "python -W ignore"
}

query(){
	echo 'ENTER some filename for query output'
	read file
	nohup python -W ignore query.py > $file &
	echo "data goes to $file"
}

remote_query(){
	echo
	echo 'default group3@199.116.235.57'
	cat  query.py | ssh -i NebulaLaunchKey.pem group3@199.116.235.57 "python -W ignore"
}

instance1(){
	ssh -x -i NebulaLaunchKey.pem group3@199.116.235.55
}

status(){
	ssh -i NebulaLaunchKey.pem group3@199.116.235.55 "apache-cassandra-2.0.6/bin/nodetool status"
}

zip(){
	tar -cvzf project.tgz query.py stats docs group3.sh generate.py tableFrequency.txt NebulaLaunchKey.pem README.md
}

setup(){
	array="10.1.0.104 10.1.0.105 10.1.0.107 10.1.0.108 10.1.0.109 10.1.0.110 10.1.0.111 10.1.0.112"
	for i in $array; do
	    ssh $i "rm -f /home/group3/cassandra/conf/cassandra.yaml"
	    sed "s/localhost/$i/g" docs/cassandra.yaml | ssh $i "cat > /home/group3/cassandra/conf/cassandra.yaml"
	    ssh $i "pkill -f cassandra"
	done
	sleep 10
	for i in $array; do
	    ssh $i "/home/group3/cassandra/bin/cassandra" &
	done
}

chmod 600 NebulaLaunchKey.pem || true
read input
case $input in
	1) generate;;
	2) remote_generate;;
	3) query;;
	4) remote_query;;
	5) status;;
	6) instance1;;
	7) zip;;
	8) generate_big;;
	9) setup;;

	*) echo "exiting";;
esac

