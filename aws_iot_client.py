from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time

# No local logger since everying is likely AWS MQTT lib logger

class AwsIotClient():
   def __init__(self, client_id, aws_host, root_ca_path, cert_path, private_key_path):
      self.aws_host = aws_host
      self.root_ca_path = root_ca_path
      self.cert_path = cert_path
      self.private_key_path = private_key_path
      self.clientId = client_id
      self.topic = "meas"

      # non-WebSocket, default to 8883
      self.port = 8883

   def connect(self):
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

   def publish(self, msg_dict):
      self.myAWSIoTMQTTClient.publish(self.topic, json.dumps(msg_dict), 1)

