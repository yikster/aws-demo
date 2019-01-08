#!python

import boto3
import json
import sys

#PROFILE BUCKET REGION DYNAMODB_TABLE

PROFILE = str(sys.argv[1])
BUCKET = str(sys.argv[2])
REGION = str(sys.argv[3])
DYNAMODB_TABLE = str(sys.argv[4])

## Set sessions and api clients
session = boto3.Session(profile_name=PROFILE)

s3 = session.client('s3')
dynamodb = session.client('dynamodb')

def get_objectkeys(token=""):

    if len(token) > 0:
        response = s3.list_objects_v2(
            Bucket=BUCKET,
            #Delimiter='/',
            EncodingType='url',
            MaxKeys=1000,
            #Prefix='',
            ContinuationToken=token,
            #FetchOwner=True|False,
            #StartAfter='string',
            #RequestPayer='requester'

        )
    else:
        response = s3.list_objects_v2(
            Bucket=BUCKET,
            # Delimiter='/',
            EncodingType='url',
            MaxKeys=1000
            # FetchOwner=True|False,
            # StartAfter='string',
            # RequestPayer='requester'

        )

    return response


response = get_objectkeys()

files = 0

while 'NextContinuationToken' in response and 0 < len(response['Contents']):
    contents = response['Contents']
    for content in contents:
        files += 1
        print (files, content['Key'])
    response = get_objectkeys(response['NextContinuationToken'])

    #print(response)
## TODO FILELIST every 1000 start with prefix in bucket
## TODO DYNAMODB TABLE exist
## TODO every 100 items in batchPutItems

