import json
import boto3

def lambda_handler(event, context):
    comprehend = boto3.client('comprehend')

    # Get the input text from the event triggered by Lambda URL
    try:
        body = json.loads(event['body'])
    except (KeyError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid input: {}'.format(str(e)))
        }

    text = body.get('text', '')
    if not text:
        return {
            'statusCode': 400,
            'body': json.dumps('No text provided for sentiment analysis')
        }

    # Call Amazon Comprehend to analyze sentiment
    response = comprehend.detect_sentiment(
        Text=text,
        LanguageCode='en'  # Modify language code as needed
    )

    # Return the sentiment analysis result
    return {
        'statusCode': 200,
        'body': json.dumps({
            'Sentiment': response['Sentiment'],
            'SentimentScore': response['SentimentScore']
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
