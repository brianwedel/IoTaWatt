import argparse
import ProducerConsumerHub

def test_callback(msg):
    print("Consumer ({}) recv ({})".format(sim_id, msg)) 

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('sim_id', type=int)
    args = parser.parse_args()
    sim_id = args.sim_id

    tester = ProducerConsumerHub.Consumer('',12001)
    tester.run(test_callback)
