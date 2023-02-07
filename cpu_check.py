import boto3
import _csv
from datetime import datetime, timedelta
import datetime


def ohio():
    return "Ohio"


def virginia():
    return "Virginia"


def oregon():
    return "Oregon"


def mumbai():
    return "Mumbai"


def sydney():
    return "Sydney"


def canada():
    return "Canada-Central"


def frankfurt():
    return "Frankfurt"


def london():
    return "London"


def paris():
    return "Paris"


def ireland():
    return "Ireland"


def singapore():
    return "Singapore"


switcher = {
    "us-east-2" : ohio,
    "us-east-1" : virginia,
    "us-west-2" : oregon,
    "ap-south-1" : mumbai,
    "ap-southeast-2" : sydney,
    "ca-central-1" : canada,
    "eu-central-1" : frankfurt,
    "eu-west-2" : london,
    "eu-west-3" : paris,
    "eu-west-1" : ireland,
    "ap-southeast-1" : singapore
}


def switch(RegionCode):
    return switcher.get(RegionCode)()


account = "AWS"
# change this while getting reports
# also change the csv name below
region_in_account = ["us-east-2", "us-east-1", "us-west-2", "ap-south-1", "ap-southeast-2", "ca-central-1", "eu-central-1", "eu-west-2", "eu-west-3", "eu-west-1"]
instance_in_region = list()
servername = list()
state = list()
public_ip = list()
max_list = list()

with open('AWS_CPU_08_03_2022.csv', 'w', newline='') as file:
    writer = _csv.writer(file)
    writer.writerow(["Name", "State", "Account", "Region", "Public IP", "Instance ID", "CPU Utilization"])
    for region in region_in_account:
        region_name = switch(region)
        ec2 = boto3.resource('ec2', region)
        for instance in ec2.instances.all():
            instance_in_region.append(instance.id)
            state.append(instance.state["Name"])
            public_ip.append(instance.public_ip_address)
            for tag in instance.tags:
                if tag['Key'] == 'Name':
                    servername.append(tag["Value"])
        client = boto3.client('cloudwatch', region)
        length = len(instance_in_region)
        i = 0
        while i < length:
            response = client.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[
                            {
                            'Name': 'InstanceId',
                            'Value': instance_in_region[i]
                            },
                        ],
                        StartTime=datetime.datetime.now() - timedelta(days=5),
                        EndTime=datetime.datetime.now(),
                        # Period=86400,
                        Period=300,
                        Statistics=[
                            'Average',
                        ],
                        Unit='Percent'
                    )

            for cpu in response['Datapoints']:
              if 'Average' in cpu:
                max_list.append(cpu['Average'])
            try:
                writer.writerow([servername[i], state[i], account, region_name, public_ip[i], instance_in_region[i], max(max_list)])
            except ValueError:
                writer.writerow([servername[i], state[i], account, region_name, public_ip[i], instance_in_region[i], "NULL"])
            max_list.clear()
            i = i + 1

        instance_in_region.clear()
        servername.clear()
        public_ip.clear()
        state.clear()