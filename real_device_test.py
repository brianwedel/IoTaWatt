import socket
import time

# connects to localhost port 12001 as a "real_device"

DELIM="#-#-#"
class RealDeviceTest(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((host, port))
        self.sock.send(b'real_device' + DELIM.encode())

    def run(self):
        counter = 0
        while True:
            self.sock.send("{}{}".format(str(counter), DELIM).encode())
            counter += 1
            time.sleep(1)
 

if __name__ == "__main__":
    tester = RealDeviceTest('',12001)
    tester.run()
