import json
import boto3

def lambda_handler(event, context):
    """
    Lambda function to perform sentiment analysis using Amazon Comprehend.

    This function is triggered by a Lambda URL and expects a POST request with
    a JSON body containing a 'text' field. It uses the Amazon Comprehend service
    to detect the sentiment of the provided text and returns the result.

    Amazon Comprehend is a Natural Language Processing (NLP) service that can
    analyze text for sentiment, key phrases, language detection, and more.
    In this function, we are specifically using the sentiment analysis feature
    to determine if the input text is positive, negative, neutral, or mixed.

    Parameters:
    -----------
    event : dict
        The event object contains request details. In this case, the event will
        have a 'body' field containing a JSON payload with the 'text' to analyze.

    context : LambdaContext
        The context object provides information about the invocation, function,
        and execution environment. It is not used in this function.

    Returns:
    --------
    dict
        A response object with the HTTP status code, sentiment analysis results,
        and appropriate headers for content type and CORS.
    """

    # Create a client to interact with the Amazon Comprehend service
    comprehend = boto3.client('comprehend')

    # Step 1: Parse the input text from the Lambda event body
    try:
        # The event body should contain the input text in JSON format
        body = json.loads(event['body'])
    except (KeyError, json.JSONDecodeError) as e:
        # If the body is missing or invalid, return a 400 Bad Request response
        return {
            'statusCode': 400,
            'body': json.dumps(f'Invalid input: {str(e)}')
        }

    # Step 2: Extract the 'text' field from the parsed body
    # The text to be analyzed must be provided under the 'text' key
    text = body.get('text', '')

    # Step 3: Validate the input to ensure text has been provided
    if not text:
        # If no text is provided, return an error response
        return {
            'statusCode': 400,
            'body': json.dumps('No text provided for sentiment analysis')
        }

    # Step 4: Call Amazon Comprehend to analyze the sentiment of the input text
    try:
        # Sentiment analysis supports multiple languages, so you must specify
        # the language code (in this case, 'en' for English).
        response = comprehend.detect_sentiment(
            Text=text,
            LanguageCode='en'  # Modify the language code if analyzing non-English text
        )
    except Exception as e:
        # If Comprehend fails to process the text, return a 500 error response
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error calling Comprehend: {str(e)}')
        }

    # Step 5: Extract the sentiment and sentiment score from the response
    sentiment = response.get('Sentiment', 'UNKNOWN')  # Sentiment (e.g., POSITIVE, NEGATIVE)
    sentiment_score = response.get('SentimentScore', {})  # Confidence scores for each sentiment

    # Step 6: Return the results in a JSON response with a 200 OK status
    return {
        'statusCode': 200,
        'body': json.dumps({
            'Sentiment': sentiment,             # The overall sentiment of the input text
            'SentimentScore': sentiment_score   # Detailed confidence scores for each sentiment
        }),
        'headers': {
            'Content-Type': 'application/json',  # Response content type
            'Access-Control-Allow-Origin': '*'   # Enable CORS for any origin
        }
    }
