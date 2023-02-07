
import boto3
import os
import json
import urllib3


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

Monitored_event = ["DescribeClusters","ListUsers","CreateBucket","DeleteBucket","DeleteBucketLifecycle","DeleteBucketPolicy","DeleteBucketTagging","ChangeResourceRecordSets","DeleteHealthCheck","AddUserToGroup","AttachGroupPolicy","AttachRolePolicy","AttachUserPolicy","ChangePassword","ConsoleLogin","CreateAccessKey","CreateAccountAlias","CreateGroup","CreateLoginProfile","CreatePolicy","CreateRole","CreateUser","CreateVirtualMFADevice","DeactivateMFADevice","DeleteAccessKey","DeleteAccountAlias","DeleteAccountPasswordPolicy","DeleteGroup","DeleteGroupPolicy","DeleteLoginProfile","DeletePolicy","DeleteRole","DeleteRolePolicy","DeleteUser","DeleteUserPolicy","DetachGroupPolicy","EnableMFADevice","RemoveUserFromGroup","UpdateUser","AuthorizeSecurityGroupIngress","AuthorizeSecurityGroupIngress","RevokeSecurityGroupEgress","RevokeSecurityGroupIngress","CreateSecurityGroup","DeleteSecurityGroup","DetachVolume","StopInstances","TerminateInstances","StopLogging"]


region_in_account = ["us-east-2", "us-east-1", "us-west-2", "ap-south-1", "ap-southeast-2", "ca-central-1", "eu-central-1", "eu-west-2", "eu-west-3", "ap-southeast-1"]

# previous_time = os.environ['Time']
# old_highest_time = os.environ['Time']
previous_time = "2021-03-26 18:00:03+05:30"
old_highest_time = "2021-03-26 18:00:03+05:30"


for region in region_in_account:
        count_of_page = 0
        ct = boto3.client('cloudtrail', region)
        paginator = ct.get_paginator('lookup_events')
        page_iterator = paginator.paginate()
        # region_name = switch(region)
        for response in page_iterator:
                count_of_page = count_of_page + 1
                length = len(response["Events"])
                print(length)
                i = length - 1
                recent_time = response["Events"][0]["EventTime"]
                recent_string_time = str(recent_time)
                if(recent_string_time < previous_time):
                        print("Break")
                        break
                elif(recent_string_time > old_highest_time) & (count_of_page == 1):
                        old_highest_time = recent_string_time
                        print("Reached")

                while i > 0:
                        time = response["Events"][i]["EventTime"]
                        string_time = str(time)
                        if(string_time < previous_time):
                                break
                        #print("Entered")
                        eventName = response["Events"][i]["EventName"]
                        for event in Monitored_event:
                                if eventName != event:
                                        continue
                                print("Entered")
                                try:
                                    Username = response["Events"][i]["Username"]
                                except KeyError:
                                    Username = "-"
                                string = response["Events"][i]['CloudTrailEvent']
                                json_data = json.loads(string)
                                ip = json_data["sourceIPAddress"]
                                Activity = json_data["requestParameters"]
                                region_name = json_data["awsRegion"]
                                try:
                                    useragent = json_data["userAgent"]
                                except KeyError:
                                    useragent = "-"
                                body = {
                                    "EventTime" : str(time),
                                    "EventSource" : response["Events"][i]["EventSource"],
                                    "EventName" : eventName,
                                    "Username" : Username,
                                    "Region" : region_name,
                                    "SourceIPAddress" : ip,
                                    "UserAgent" : useragent,
                                    "DetailedActivity" : Activity

                                }
                                encoded_body = json.dumps(body).encode('utf-8')
                                http = urllib3.PoolManager()
                                r = http.request('POST', 'https://licensing.paradisolms.net/cloudmonitoring.php',
                                                headers={'Content-Type': 'application/json'},
                                                body=encoded_body)

                                print(r.status)
                        i = i - 1

print(old_highest_time)



