import json
import boto3
import re
import os

collection_id = os.environ['COLLECTION_ID']
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name = 'ap-northeast-1')
        
def remove_invalid_chars(key):
    #Removes invalid characters from a key.
    regex = re.compile('[^a-zA-Z0-9_.\-:]+')
    key = regex.sub('', key)
    return key

def lambda_handler(event, context):
    print(event)
    # Get the S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Detect faces in the image
    try:
        response = rekognition.index_faces(
            CollectionId = collection_id,
            Image = {'S3Object':
                    {
                        'Bucket': bucket,
                        'Name': key
                    }
                },
            ExternalImageId = remove_invalid_chars(key),
            MaxFaces = 10
            )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        # Return JSON
            return json.dumps(response)
    except Exception as e:
        print(e)
        print('Error processing image {} from bucket {}.'.format(key,bucket))
        raise e
