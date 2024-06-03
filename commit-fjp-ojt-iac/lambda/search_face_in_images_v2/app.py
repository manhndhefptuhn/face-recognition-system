import json
import boto3
import os
import requests


rekognition_client = boto3.client('rekognition', region_name = 'ap-northeast-1')
dynamodb_client = boto3.client('dynamodb')

# Set variable in lambda function's configuration
collection_id = os.environ.get('REKOGNITION_COLLECTION', 'face-collection')
dynamodb_table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'myRekognitionRecord')

# Query DynamoDB to get user information based on the recognized face
def get_user_info(table_name, face_id):
    response = dynamodb_client.get_item(
        TableName=table_name,
        Key={'FaceId': {'S': face_id}}
    )
    return response.get('Item')

#Split the URI receive from the UI
def split_s3_uri(s3_uri):
    s3_parts = s3_uri.replace("s3://", "").split('/')

    bucket_name = s3_parts[0]
    object_key = "/".join(s3_parts[1:])

    return bucket_name, object_key

def lambda_handler(event, context):
    try:
        # Retrieve the S3 object URI from the event
        s3_object_uri = event['body']['s3_object_uri']
        
        bucket_name, object_key = split_s3_uri(s3_uri)

        image = {
        'S3Object': {
            'Bucket': bucket_name,
            'Name': object_key
            }
        }

        # Search for faces in the image using Rekognition
        response = rekognition_client.search_faces_by_image(
            CollectionId=collection_id,
            Image=image,
            MaxFaces=5
        )
        
        # Process the search results (similar faces)
        faces = response.get('FaceMatches', [])

        result = []

        for face in faces:
            face_id = face['Face']['FaceId']
            similarity = face['Similarity']

            # Get user information from DynamoDB based on the recognized face
            user_info = get_user_info(dynamodb_table_name, face_id)

            if user_info:
                result.append({
                    'FaceId': face_id,
                    'Similarity': similarity,
                    'UserInfo': user_info
                })

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

   









# # faces = response.get('FaceMatches', [])

#     # Process the response and take appropriate actions
#     if 'FaceMatches' in response:
#             results = []

#         for match in response['FaceMatches']:
#             face_id = match['Face']['FaceId']
#             similarity = match['Similarity']

#             # Now, search for user information in DynamoDB using the face_id
#             user_info = search_user_info_in_dynamodb(dynamodb_table_name, face_id)

#             if user_info:
#                 result = {
#                     'FaceId': face_id,
#                     'Similarity': similarity,
#                     'UserInfo': user_info
#                 }
#                 results.append(result)

#         # Return the results to the same Lambda function
#         return results

#         result = []
#         for face in faces:
#             result.append({
#                 'FaceId': face['Face']['FaceId'],
#                 'Similarity': face['Similarity']
#             })
