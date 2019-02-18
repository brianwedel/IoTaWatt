import time
import sys
from daemon import Daemon

class DaemonTest(Daemon):
   def run(self):
      while True:
         print("test!")
         time.sleep(1)   

if __name__ == "__main__":
   d = DaemonTest('/tmp/bwedel.pid')
   if len(sys.argv) == 2:
      if 'start' == sys.argv[1]:
         d.start()
      elif 'stop' == sys.argv[1]:
         d.stop()
      elif 'restart' == sys.argv[1]:
         d.restart()
      else:
         print "Unknown command"
         sys.exit(2)
      sys.exit(0)
   else:
      print "usage: %s start|stop|restart" % sys.argv[0]
      sys.exit(2)
