import json
import boto3
import pandas as pd

def lambda_handler(event, context):
    
    sns_topic_arn = "arn:aws:sns:us-east-1:381492087220:first-topic"
    s3_source_bucket = 'doordash-landing-zn-assign'
    s3_source_object_key = event['Records'][0]['s3']['object']['key']
    
    s3_target_bucket = 'doordash-target-zn-assign'
    s3_target_object_key = s3_source_object_key
    
    s3 = boto3.client('s3')
    sns_client = boto3.client('sns')
    try:
        message = "Lambda function execution successful!"
        # Read the json from source bucket
        s3_object = s3.get_object(Bucket=s3_source_bucket, Key=s3_source_object_key)
        file_content = s3_object['Body'].read()
        json_data = json.loads(file_content)
        df = pd.DataFrame(columns= ["id","status","amount","date"])
        for i in range(0, len(json_data)):
            df.loc[i] = [json_data[i]["id"],json_data[i]["status"],json_data[i]["amount"],json_data[i]["date"]]
        
        # filter the records based on status = 'delivered'
        df2 =df[df['status'] =='delivered']
        json_content = df2.to_json( orient= 'records', date_format='iso') 
        # write the json file into target bucket
        s3.put_object(Bucket=s3_target_bucket, Key=s3_target_object_key, Body=json_content.encode('utf-8'))
        
        
    
    except Exception as e:
        message = f"Lambda function execution failed: {str(e)}"

    response = sns_client.publish(
    TopicArn=sns_topic_arn,
    Message=message
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Json file filtering!')
    }
