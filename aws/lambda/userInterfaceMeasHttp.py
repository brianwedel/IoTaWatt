import json
import time
import decimal

import boto3
from boto3.dynamodb.conditions import Key, Attr

print('Loading function')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('wellshire-testbed-agg2')

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
        
def respond(err_msg, res=None):
    return {
        'statusCode': '400' if err_msg else '200',
        'body': err_msg if err_msg else json.dumps(res, cls=DecimalEncoder),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def get_agg_data(house_id, today):
    
    response = table.query(
        KeyConditionExpression=Key('house_id').eq(house_id) & Key('date_time').begins_with("{}".format(today))
    )
    
    total_energy_kwh = decimal.Decimal(0.0)
    max_power = []
    avg_power = []
    for i in response["Items"]:
        total_energy_kwh += i["energy_kwh"]
        max_power.append(i["max_power_watt"])
        avg_power.append(i["avg_power"])
        
    
    date_str = time.strftime("%a, %d %b %Y", time.gmtime(today))

    return {
        'total_energy_kwh': total_energy_kwh,
        'max_power': max_power,
        'avg_power': avg_power,
        'house_id': house_id,
        'date_str' : date_str
    }
        
        
    
def get_today():
    timezone_offset_hrs = -7.0 # America/Denver (this should eventually come from the DB)
    tz_offset_sec = timezone_offset_hrs*3600 
    sec_per_day = 86400.0 # Unix time has exactly 86400 seconds per day
    # Shift unix time reference to align with local timezone for day boundary alignment, then undo shift
    # to produce unix timestamp that aligns with start of today in the local timezone
    today_start_timestamp = int((time.time() + tz_offset_sec) / sec_per_day) * sec_per_day - tz_offset_sec
    
    return int(today_start_timestamp)
    

def lambda_handler(event, context):
    '''Query wellshire-testbed-agg2 table for power data for current day
    '''

    today_start_timestamp = get_today()
    
    if event["queryStringParameters"] and "house_id" in event["queryStringParameters"]:
        house_id = event["queryStringParameters"]["house_id"]
        return respond(None, get_agg_data(house_id, today_start_timestamp))
    else:
        return respond('Need to provide house_id', None)
