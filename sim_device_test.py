import socket
import time
import argparse

# connects to localhost port 12001 as a "sim_device"

DELIM="#-#-#"
class SimDeviceTest(object):
    def __init__(self, host, port, id):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((host, port))
        self.sock.send(b'sim_device' + DELIM.encode())
        self.id = id

    def run(self):
        counter = 0
        while True:
            data = self.sock.recv(1024)
            print("Sim ({}) got data ({})".format(self.id, data))
 

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('sim_id', type=int)
    args = parser.parse_args()

    tester = SimDeviceTest('',12001, args.sim_id)
    tester.run()
