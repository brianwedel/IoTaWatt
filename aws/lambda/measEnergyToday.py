import functools
import json
import time
import decimal

import boto3
import botocore

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('wellshire-testbed-agg2')

"""
Trigger each MQTT meas topic and aggregate samples into per user#day DB record
"""
    
# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    power_samples = [s["channel1_power_meas"] + s["channel2_power_meas"] for s in event["samples"]]
    max_power = max(power_samples)
    avg_power = sum(power_samples)/float(len(power_samples))
    duration_sec = (event["samples"][-1]["meas_time_ms"] - event["samples"][0]["meas_time_ms"])/1000.0
    # simple integration over all the samples (note assume sample period of 250 ms)
    energy_kwh = round(functools.reduce(lambda a, b: a+b*.250, power_samples)/(1000.0*60*60), 7)
    
    timezone_offset_hrs = -7.0 # America/Denver (this should eventually come from the DB)
    tz_offset_sec = timezone_offset_hrs*3600 
    sec_per_day = 86400.0 # Unix time has exactly 86400 seconds per day
    # Shift unix time reference to align with local timezone for day boundary alignment, then undo shift
    # to produce unix timestamp that aligns with start of today in the local timezone
    today_start_timestamp = int((time.time() + tz_offset_sec) / sec_per_day) * sec_per_day - tz_offset_sec
    
    # Figure out into which time bucket to aggregate the event 
    bucket_duration_sec = 360.0
    bucket_idx = int((event["timestamp"]/1000.0 - today_start_timestamp)/bucket_duration_sec)
    
    # Pull aggregation record for house_id + day#time
    house_id = event["house_id"]
    date_time = "{}#{:03d}".format(int(today_start_timestamp), bucket_idx)

    
    try:
        response = table.get_item(
            Key={
                'house_id': house_id,
                'date_time': date_time
            })
    except botocore.exceptions.ClientError as e:
        print(e.response['Error']['Message'])
    else:
        # Check to see if an Item was returned from the DB. If not,
        # create a new, empty data structure
        if "Item" in response:
            b = response["Item"]
        else:
            b = {
                'house_id': house_id,
                'date_time': date_time,
                'max_power_watt': decimal.Decimal(0.0),
                'avg_power_watt_sum': decimal.Decimal(0.0),
                'avg_power_watt_num_samples': 0,
                'energy_kwh': decimal.Decimal(0.0)
            }
        
        # Update aggregated power data in the bucket
        if max_power > b["max_power_watt"]:
            b["max_power_watt"] = decimal.Decimal(max_power)
        b["energy_kwh"] += decimal.Decimal(energy_kwh)
        b["avg_power_watt_sum"] += decimal.Decimal(avg_power)
        b["avg_power_watt_num_samples"] += 1
        b["avg_power"] = b["avg_power_watt_sum"] / b["avg_power_watt_num_samples"]
        
        # push updated record back to db
        try:
            response = table.put_item(Item=b)
        except botocore.exceptions.ClientError as e:
            print(e.response['Error']['Message'])
            
    return 0
