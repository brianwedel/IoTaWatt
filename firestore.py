import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import time
import socket
import json
import logging

# Proxy server for Firestore database
# Listen for UDP datagrams on port 12000, expecting a JSON string payload
# Read JSON into a dictionary and set into the Firestore database
# Proxy server is meant to be a pass through for data payload and creates
# a new Firestore db document for each received payload.  The proxy server
# uses the local time (ms) as the document name

def reset_accum_samples():
    current_time_ms = int(round(time.time() * 1000))
    accum_samples = {
        "start_time_ms" : current_time_ms,
        "samples" : []}
    return accum_samples

logging.basicConfig(
    filename='firestore.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s')

# Connect to firestore database
cred = credentials.Certificate('../wellshire-testbed-firebase-adminsdk-cdfa8-ade79ce610.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Create server socket
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Assign IP address and port number to socket
soc.bind(('', 12000))

# Server loop to forward data to firestore database
first_sample = True
while True:
    # Receive the client packet along with the address it is coming from
    message, address = soc.recvfrom(1024)
    if first_sample:
        accum_samples = reset_accum_samples()
        first_sample = False

    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        logging.error("Invalid data payload {}".format(message))

    current_time_ms = int(round(time.time() * 1000))    
    accum_samples["samples"].append(data)

    if len(accum_samples["samples"]) >= 40:
        try:
            doc_ref = db.collection(u'house').document(u'kTwB5pLnvThWmqcqIvaU').collection('meas').document(
                str(accum_samples["start_time_ms"]))
            doc_ref.set(accum_samples)
        except Exception as e:
            logging.error("Exception occured while interacting with Firestore: " + str(e))
            logging.error(traceback.format_exc())

        # reset first sample flag
        first_sample = True
