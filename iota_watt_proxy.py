'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''
from daemon import Daemon
from aws_iot_client import AwsIotClient
import ProducerConsumerHub
import logging
import time
import argparse
import json
import socket

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
         accum_samples = reset_accum_samples()

         for s in range(0, 40):
            # Receive the client packet along with the address it is coming from
            message, address = soc.recvfrom(1024)
            try:
               data = json.loads(message)
            except json.JSONDecodeError:
               logging.error("Invalid data payload {}".format(message))
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
            logging.error("Exception occured while publishing to AWS IOT: " + str(e))

if __name__ == "__main__":

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
   HOUSE_ID = "7905 Wellshire Ct"
