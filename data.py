import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('wellshire-testbed-agg2')

today="1550646000"
data = {}

for node_id in range(1,31):
   house_id="replicator{}".format(node_id)

   response = table.query(
      KeyConditionExpression=Key('house_id').eq(house_id) & Key('date_time').begins_with("{}".format(today))
   )

   data[house_id] = response["Items"]


def compare_dict(d1, d2):
   diffkeys = [k for k in d1 if d1[k] != d2[k] and k != "house_id"]
   for k in diffkeys:
      print("{} : {} != {}".format(k, d1[k], d2[k]))

ref_key = "replicator1"
reference = data[ref_key]
for key, val in data.items():
   print("Compare({}, {})".format(ref_key, key))
   for m1, m2 in zip(reference, val): 
      compare_dict(m1, m2) 
   
