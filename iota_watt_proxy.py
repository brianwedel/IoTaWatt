from daemon import Daemon
from aws_iot_client import AwsIotClient
import ProducerConsumerHub
import logging
import time
import argparse
import json
import socket

myLogger = logging.getLogger(__name__)

class IotaWattProxy(Daemon, AwsIotClient):
   def __init__(self, house_id, client_id, aws_host, root_ca_path, cert_path, private_key_path, pid_file):
      Daemon.__init__(self, pid_file)
      AwsIotClient.__init__(self, client_id, aws_host, root_ca_path, cert_path, private_key_path)

      self.house_id = house_id

   def reset_accum_samples(self):
      current_time_ms = int(round(time.time() * 1000))
      accum_samples = {
          "house_id" : self.house_id,
          "timestamp" : current_time_ms,
          "samples" : []}

      return accum_samples

   # Daemon entry point
   def run(self):

      # Connect to AWS Iot Core
      self.connect()

      # Create server socket
      soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

      # Assign IP address and port number to socket
      soc.bind(('', 12000))

      # Server loop to forward data to firestore database
      first_sample = True
     
      # Connect to replication prod/cons hub
      replication_prod = ProducerConsumerHub.Producer('', 12001)

      # Server loop to forward data to firestore database
      while True:
         # Reset sample struct each 40 samples    
         accum_samples = self.reset_accum_samples()

         for s in range(0, 40):
            # Receive the client packet along with the address it is coming from
            message, address = soc.recvfrom(1024)
            try:
               data = json.loads(message)
            except json.JSONDecodeError:
               myLogger.error("Invalid data payload {}".format(message))
               data = {}

            accum_samples["samples"].append(data)

         # At the end of sample accumulation, foward onto AWS IOT core
         try:
            # Publish to IOT core
            self.publish(accum_samples)
            # Publish to producer/consumer hub
            messageJson = json.dumps(accum_samples)
            replication_prod.send_msg(messageJson)
         except Exception as e:
            myLogger.error("Exception occured while publishing to AWS IOT: " + str(e))

if __name__ == "__main__":

   HOUSE_ID = "7905 Wellshire Ct"

   # Configure logging
   fh = logging.FileHandler('/tmp/iotawatt_proxy.log')
   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   fh.setFormatter(formatter)

   logger = logging.getLogger("AWSIoTPythonSDK.core")
   logger.setLevel(logging.INFO)
   logger.addHandler(fh)

   # deamon logger catches exceptions in Daemon.run()
   daemon_logger = logging.getLogger("daemon")
   daemon_logger.setLevel(logging.INFO)
   daemon_logger.addHandler(fh)

   iota_watt_proxy_logger = logging.getLogger("iota_watt_proxy")
   iota_watt_proxy_logger.setLevel(logging.INFO)
   iota_watt_proxy_logger.addHandler(fh)

   parser = argparse.ArgumentParser(description='IotaWatt AWS proxy')
   parser.add_argument('command', type=str, choices=['start','stop'])
   args = parser.parse_args()

   # Constant input params
   aws_host = 'a5zxmnr1dzhfm-ats.iot.us-west-2.amazonaws.com'
   root_ca_path = '/local/wellshire-testbed/aws_iot_cred/AmazonRootCA1.pem'
   cert_path = '/local/wellshire-testbed/aws_iot_cred/68f6251505-certificate.pem.crt'
   private_key_path = '/local/wellshire-testbed/aws_iot_cred/68f6251505-private.pem.key'

   d = IotaWattProxy(
      HOUSE_ID,
      'basicPubSub',
      aws_host,
      root_ca_path,
      cert_path,
      private_key_path,
      '/tmp/iotawatt_proxy.pid')

   if args.command == "start": 
      d.start()
   elif args.command == "stop":
      d.stop()

