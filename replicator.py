import ProducerConsumerHub
import logging
import time
import json
from daemon import Daemon
from aws_iot_client import AwsIotClient

'''
Replicate data published to the producer/consumer hub and send into AWS IoT core with different House ID
'''
class HouseReplicator(Daemon, AwsIotClient):
   def __init__(self, house_id, client_id, aws_host, root_ca_path, cert_path, private_key_path, pid_file):
      Daemon.__init__(self, pid_file)
      AwsIotClient.__init__(self, client_id, aws_host, root_ca_path, cert_path, private_key_path)

      self.house_id = house_id

   def consumer_callback(self, msg):
      msg_dict = json.loads(msg)
      msg_dict["house_id"] = self.house_id
      try:
         self.publish(msg_dict)
      except Exception as e:
         logging.error("Exception occured {}".format(str(e)))

   def run(self):
      # Connect to Aws Iot Core
      self.connect()

      # Connect to replication prod/cons hub as a consumer
      replication_cons = ProducerConsumerHub.Consumer('', 12001)
      replication_cons.run(self.consumer_callback)
