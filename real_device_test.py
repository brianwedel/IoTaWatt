import time

import ProducerConsumerHub

prod = ProducerConsumerHub.Producer('', 12001)
counter = 0
while True:
   prod.send_msg("{}".format(counter))
   counter += 1
   time.sleep(1)
