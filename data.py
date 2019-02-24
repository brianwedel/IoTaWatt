import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('wellshire-testbed-agg2')

today="1550905200"
data = {}

for node_id in range(1,31):
   house_id="replicator{}".format(node_id)

   response = table.query(
      KeyConditionExpression=Key('house_id').eq(house_id) & Key('date_time').begins_with("{}".format(today))
   )

   data[house_id] = response["Items"]


def compare_dict(d1, d2):
   diffkeys = [k for k in d1 if d1[k] != d2[k] and k not in ["house_id", "dup_detect_request_id"]]
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
   
