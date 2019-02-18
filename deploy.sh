PYTHON=../venv/bin/python
#../venv/bin/python ./aws_iot_proxy.py -e a5zxmnr1dzhfm-ats.iot.us-west-2.amazonaws.com -r /tmp/AmazonRootCA.pem -c /tmp/68f6251505-certificate.pem.crt -k /tmp/68f6251505-private.pem.key
CMD=$1

function hub_ctrl() {
   # Start stop Producer/consumer hub
   $PYTHON ./ProducerConsumerHub.py $CMD
}

function replicator_ctrl() {
   NUM_REPLICATOR=10
   for i in `seq 1 $NUM_REPLICATOR`; do
      $PYTHON ./replicator_daemon.py $i $CMD
   done
}

function iotawatt_proxy_ctrl() {
   echo "test"
   #$PYTHON ./aws_iot_proxy.py $CMD
}

# Order of start/stop is important since the replicators
# and iotawatt proxy connect to the hub.
if [ "$CMD" = "start" ]; then
   hub_ctrl
   replicator_ctrl
   iotawatt_proxy_ctrl
elif [ "$CMD" =  "stop" ]; then
   iotawatt_proxy_ctrl
   replicator_ctrl
   hub_ctrl
else
   echo "Invalid command $CMD"
   exit 1
fi
