import boto3
from boto3.dynamodb.conditions import Key, Attr

import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('wellshire-testbed-v2-agg')

data = {}

timezone_offset_hrs = -7.0 # America/Denver (this should eventually come from the DB)
tz_offset_sec = timezone_offset_hrs*3600 
sec_per_day = 86400.0 # Unix time has exactly 86400 seconds per day
# Shift unix time reference to align with local timezone for day boundary alignment, then undo shift
# to produce unix timestamp that aligns with start of today in the local timezone
today_start_timestamp = int((time.time() + tz_offset_sec) / sec_per_day) * sec_per_day - tz_offset_sec
    
# convert to bucket index
bucket_size = 3*60*1000 # hard coded from meas-proc-v2 event handler
start_bucket_idx = int((today_start_timestamp * 1000)/bucket_size)

for node_id in range(1,11):
   house_id="replicator{}".format(node_id)

   response = table.query(
      KeyConditionExpression=Key('house_id').eq(house_id) & Key('bucket_idx').gte(start_bucket_idx)
   )

   if len(response["Items"]) > 0:
      data[house_id] = response["Items"]


def compare_dict(d1, d2):
   diffkeys = [k for k in d1 if d1[k] != d2[k] and k not in ["house_id"]]
   for k in diffkeys:
      print("{} : {} != {}".format(k, d1[k], d2[k]))
   return len(diffkeys)

for ref_key, ref_val in data.items():
   for key, val in data.items():
      print("Compare({}, {})".format(ref_key, key))
      print("Length({}, {})".format(len(ref_val), len(val)))
      count = 0
      # skip last element because it's the active time bucket
      for m1, m2 in zip(ref_val[:-1], val[:-1]): 
         mismatch = compare_dict(m1, m2)
         if mismatch > 0:
             print("MISMATCH index {} {}\n{}".format(count, m1, m2))
         count += 1 
   
