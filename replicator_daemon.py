from replicator import HouseReplicator
import sys
import argparse
import logging

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('instance', type=int)
parser.add_argument('command', type=str, choices=['start','stop'])
args = parser.parse_args()

# Constant input params
aws_host = 'a5zxmnr1dzhfm-ats.iot.us-west-2.amazonaws.com'
root_ca_path = '/tmp/AmazonRootCA.pem'
cert_path = '/tmp/6338467ca1-certificate.pem.crt'
private_key_path = '/tmp/6338467ca1-private.pem.key'

# Incrementing input params
house_id_base = 'replicator{}'
client_id_base = 'replicatorClient{}'
pid_file = '/tmp/replicator_daemon{}.pid'

 # Configure logging
fh = logging.FileHandler("/tmp/replicator{}.log".format(args.instance))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.INFO)
logger.addHandler(fh)

# deamon logger catches exceptions in Daemon.run()
daemon_logger = logging.getLogger("daemon")
daemon_logger.setLevel(logging.INFO)
daemon_logger.addHandler(fh)

d = HouseReplicator(
      house_id_base.format(args.instance),
      client_id_base.format(args.instance),
      aws_host,
      root_ca_path,
      cert_path,
      private_key_path,
      pid_file.format(args.instance))

if args.command == "start": 
   d.start()
elif args.command == "stop":
   d.stop()
