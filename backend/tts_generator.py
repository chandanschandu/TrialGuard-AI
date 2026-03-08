import os
import boto3
from dotenv import load_dotenv

load_dotenv()

polly = boto3.client('polly', region_name=os.getenv('AWS_REGION', 'us-east-1'))
s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))

def generate_tts(text, session_id, lang='en'):
    # Aditi for Hindi, Joanna for English
    voice = 'Aditi' if lang == 'hi' else 'Joanna'
    
    response = polly.synthesize_speech(
        OutputFormat='mp3',
        VoiceId=voice,
        Text=text,
        Engine='neural' if voice == 'Joanna' else 'standard'
    )
    
    bucket = os.getenv('S3_BUCKET')
    s3_key = f"audio/dr_protocol_{session_id}.mp3"
    
    s3.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=response['AudioStream'].read(),
        ContentType='audio/mpeg'
    )
    
    return f"https://{bucket}.s3.amazonaws.com/{s3_key}"
