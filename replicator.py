import ProducerConsumerHub
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import json
from daemon import Daemon

'''
Replicate data published to the producer/consumer hub and send into AWS IoT core with different House ID
'''

class HouseReplicator(Daemon):
   def __init__(self, house_id, client_id, aws_host, root_ca_path, cert_path, private_key_path, pid_file):
      super().__init__(pid_file)
      self.house_id = house_id
      self.aws_host = aws_host
      self.root_ca_path = root_ca_path
      self.cert_path = cert_path
      self.private_key_path = private_key_path
      self.clientId = client_id
      self.topic = "meas"

      # non-WebSocket, default to 8883
      self.port = 8883

   def consumer_callback(self, msg):
      msg_dict = json.loads(msg)
      msg_dict["house_id"] = self.house_id
      try:
         self.myAWSIoTMQTTClient.publish(self.topic, json.dumps(msg_dict), 1)
      except Exception as e:
         logging.error("Exception occured {}".format(str(e)))

   def run(self):
      # Init AWSIoTMQTTClient
      self.myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId)
      self.myAWSIoTMQTTClient.configureEndpoint(self.aws_host, self.port)
      self.myAWSIoTMQTTClient.configureCredentials(self.root_ca_path, self.private_key_path, self.cert_path)

      # AWSIoTMQTTClient connection configuration
      self.myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
      self.myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
      self.myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
      self.myAWSIoTMQTTClient.configureConnectDisconnectTimeout(20)  # 10 sec
      self.myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

      # Connect to AWS IoT
      self.myAWSIoTMQTTClient.connect()
      time.sleep(2)

      # Connect to replication prod/cons hub as a consumer
      replication_cons = ProducerConsumerHub.Consumer('', 12001)
      replication_cons.run(self.consumer_callback)
