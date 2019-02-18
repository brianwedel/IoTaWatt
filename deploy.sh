#./venv/bin/python ./ProducerConsumerHub.py
#../venv/bin/python ./aws_iot_proxy.py -e a5zxmnr1dzhfm-ats.iot.us-west-2.amazonaws.com -r /tmp/AmazonRootCA.pem -c /tmp/68f6251505-certificate.pem.crt -k /tmp/68f6251505-private.pem.key
CMD=$1
NUM_REPLICATOR=10
for i in `seq 1 $NUM_REPLICATOR`; do
   ../venv/bin/python ./replicator_daemon.py $i $CMD
done
