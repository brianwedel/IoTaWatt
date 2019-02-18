from daemon import Daemon
import socket
import threading
import argparse

'''
# Server listens to port 12001, supports connection of 1 producer and >=1 consumers.
# Server forwards any data from producer to all connected consumers 
# Producer and consumer can be dynamically added and released 

Communication protocol
 - first message from either producer or consumer must be string "producer" or "consumer"
 - messages are delimited by the character sequence #-#-#
'''

CMD_DELIM="#-#-#"
CONSUMER_CMD="consumer"
PRODUCER_CMD="producer"

class Producer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((host, port))
        self.sock.send(PRODUCER_CMD.encode() + CMD_DELIM.encode())

    def send_msg(self, msg):
        self.sock.sendall(msg.encode() + CMD_DELIM.encode())

class Consumer(object):
    def __init__(self, host, port, id=0):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((host, port))
        self.sock.send(CONSUMER_CMD.encode() + CMD_DELIM.encode())
        self.id = id

    def run(self, callback):
        left_over_msg_str = ''
        while True:
            data = self.sock.recv(1024)
            if data:
                cmd_array = Hub.parse_data(data, left_over_msg_str)
                left_over_msg_str = cmd_array.pop(-1)
                # if there are full commands, remove delimiter and invoke callback
                if len(cmd_array) > 0:
                    for msg in cmd_array:
                        msg.replace(CMD_DELIM, '')
                        callback(msg)
            else:
                 print("No data from hub, exiting...")
                 break


class Hub(Daemon):
    def __init__(self, host, port, pid_file):
        super().__init__(pid_file)
        self.host = host
        self.port = port
        self.client_sock_lock = threading.Lock()
        self.consumer_list = []
        self.producer_connected = False

    # Daemon entry point
    def run(self):
        self.connect()
        return self.listen()

    def connect(self): 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def parse_data(byte_data, prev_data_str):
       all_data = prev_data_str.encode() + byte_data
       return all_data.decode().split(CMD_DELIM)

    def listen(self):
        size = 1024
        self.sock.listen(5)
        left_over_data_str = ''
        while True:
            client, address = self.sock.accept()
            try:
               data = client.recv(size)
               cmd_array = Hub.parse_data(data, left_over_data_str)
               # try to extract full command
               if cmd_array[-1] == '':
                  first_cmd = cmd_array.pop(0)

                  # if client identifies as the one allowed produced, spawn handler thread
                  if first_cmd == "producer":
                     assert(not self.producer_connected)
                     self.producer_connected = True
                     print("Producer connected.")
                     thread_type = self.listenToProducer
                     threading.Thread(target=self.listenToProducer, args=(client, cmd_array)).start()

                  # if client identifies as a consumer, add socket to
                  # shared list to be serviced buy the producer listener thread
                  elif first_cmd == "consumer":
                     with self.client_sock_lock:
                        self.consumer_list.append(client)
                     print("HUB: consumer connected (total={})".format(len(self.consumer_list)))
                  else:
                     raise ValueError("invalid first command from client ({})".format(data))

               else:
                  # If we don't have a full command, continue listening for data
                  assert(len(cmd_array) == 1)
                  left_over_data_str = cmd_array[0]
                  continue

            except Exception as e:
               print("Error " + str(e))

    def service_consumer(self, client, data): 
        try:
            client.sendall(data)
            return True
        except Exception as e:
            print("Error occured while trying to send data to consumer, removing from list".format(str(e)))
            # Assume device endoint is no longer working ... remove from list
            return False

    def listenToProducer(self, client, cmd_array):
        size = 1024
        while True:
            data = client.recv(size)
            if data:
                # Duplicate data to all connected consumers
                with self.client_sock_lock:
                    self.consumer_list = \
                        [x for x in self.consumer_list if self.service_consumer(x, data)]
            else:
               print("No data from producer, terminating producer thread.")
               self.producer_connected = False
               return False

if __name__ == "__main__":
    # Daemon control interface
    parser = argparse.ArgumentParser(description='Single Producer/Multi Consumer message passing hub server (localhost:12001)')
    parser.add_argument('command', type=str, choices=['start','stop'])
    args = parser.parse_args()
    d = Hub('',12001, '/tmp/hub.pid')

    if args.command == "start":
       d.start()
    elif args.command == "stop":
       d.stop()
