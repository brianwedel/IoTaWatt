import socket
import threading

'''
# Server listens to port 12001, supports connection of 1 "real_device" and >=1 "sim_device".
# Server forwards any data fro the real_device to all the connected sim_devices
# sim devices can be dynamically added and released, server shuts down when real device disconnects

Communication protocol
 - first command must be real_device or sim_device
 - commands are delimited by the character #-#-#
'''

class CitySimulator(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.client_sock_lock = threading.Lock()
        self.sim_device_sock_list = []
        self.real_device_connected = False

    def parse_data(self, byte_data, prev_data_str):
       ''' data = bytes-like input with commands delimited by "#"
       '''
       CMD_DELIM="#-#-#"
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
               cmd_array = self.parse_data(data, left_over_data_str)
               # try to extract full command
               if cmd_array[-1] == '':
                  first_cmd = cmd_array.pop(0)

                  # if client identifies as the one allowed real device, spawn handler thread
                  if first_cmd == "real_device":
                     assert(not self.real_device_connected)
                     self.real_device_connected = True
                     thread_type = self.listenToProducer
                     threading.Thread(target=self.listenToProducer, args=(client, cmd_array)).start()

                  # if client identifies as one of many allowed sim devices, add socket to
                  # shared list to be serviced buy the producer listener thread
                  elif first_cmd == "sim_device":
                     with self.client_sock_lock:
                        self.sim_device_sock_list.append(client)
                  else:
                     raise ValueError("invalid first command from client ({})".format(data))

               else:
                  # If we don't have a full command, continue listening for data
                  assert(len(cmd_array) == 1)
                  left_over_data_str = cmd_array[0]
                  continue

            except Exception as e:
               print("Error " + str(e))

    def service_sim_device(self, client, data): 
        try:
            client.sendall(data)
            return True
        except Exception as e:
            print("Error occured while trying to send data to sim device, removing from list".format(str(e)))
            # Assume device endoint is no longer working ... remove from list
            return False

    def listenToProducer(self, client, cmd_array):
        size = 1024
        while True:
            data = client.recv(size)
            if data:
                print("Got data ({})".format(data))
                # Duplicate data to all connected sim device endpoints
                with self.client_sock_lock:
                    print("Forwarding to {} sim devices".format(len(self.sim_device_sock_list)))
                    self.sim_device_sock_list = \
                        [x for x in self.sim_device_sock_list if self.service_sim_device(x, data)]
            else:
               print("No data from real device, terminating producer thread.  Please reconnect real_device")
               self.real_device_connected = False
               return False

if __name__ == "__main__":
    sim = CitySimulator('',12001).listen()
