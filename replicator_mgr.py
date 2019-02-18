from replicator import HouseReplicator
import sys

NUM_REPLICATORS=1

# Constant input params
aws_host = 'a5zxmnr1dzhfm-ats.iot.us-west-2.amazonaws.com'
root_ca_path = '/tmp/AmazonRootCA.pem'
cert_path = '/tmp/6338467ca1-certificate.pem.crt'
private_key_path = '/tmp/6338467ca1-private.pem.key'

# Incrementing input params
house_id_base = 'replicator{}'
client_id_base = 'replicatorClient{}'
pid_file = '/tmp/replicator_daemon{}.pid'

nodes = []
for i in range(0, NUM_REPLICATORS):
   nodes.append(HouseReplicator(
      house_id_base.format(i),
      'basicPubSub', #client_id_base.format(i),
      aws_host,
      root_ca_path,
      cert_path,
      private_key_path,
      pid_file))

### SWITCH TO ARGPARSE
if len(sys.argv) == 2:
   if 'start' == sys.argv[1]:
      for d in nodes:
         d.start()
   elif 'stop' == sys.argv[1]:
      for d in nodes:
         d.stop()
   elif 'restart' == sys.argv[1]:
      for d in nodes:
         d.restart()
   else:
      print("Unknown command")
      sys.exit(2)

   sys.exit(0)
else:
   print("usage: {} start|stop|restart".format(sys.argv[0]))
   sys.exit(2)

