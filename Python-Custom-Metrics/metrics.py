#!/usr/bin/env python3
import boto3
import psutil
import requests
_METADATAURL = 'http://169.254.169.254/latest/meta-data' # where to obtain instance metadata ...

cw = boto3.client('cloudwatch')
currMetrics = []
def appendMetrics(CurrentMetrics, Dimensions, Name, Unit, Value):
    metric = { 'MetricName' : Name
    , 'Dimensions' : Dimensions
    , 'Unit' : Unit
    , 'Value' : Value
    }
    CurrentMetrics.append(metric)

def memUsedByApache():
    return round(sum([p.info['memory_info'].rss for p in psutil.process_iter(attrs=['name','memory_info']) if 'httpd' in p.info['name']]) / (1024*1024), 1)

def usedMemoryPercentage():
    return psutil.virtual_memory().percent

def usedDiskSpace():
    return psutil.disk_usage('/').percent

if __name__ == '__main__':
    instance_id = requests.get( _METADATAURL + '/instance-id').text
    instance_type = requests.get( _METADATAURL + '/instance-type').text
    dimensions = [{'Name' : 'InstanceId', 'Value': instance_id}, {'Name' : 'InstanceType', 'Value': instance_type}]
    appendMetrics(currMetrics, dimensions, Name='ApacheMemory', Value=memUsedByApache(), Unit='Megabytes')
    appendMetrics(currMetrics, dimensions, Name='MemoryInUse', Value=usedMemoryPercentage(), Unit='Percent')
    appendMetrics(currMetrics, dimensions, Name='DiskspaceUsed', Value=usedDiskSpace(), Unit='Percent')

    response = cw.put_metric_data(MetricData = currMetrics, Namespace='CustomMetrics')
