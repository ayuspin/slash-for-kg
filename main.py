import requests
import json
from flask import jsonify
import hmac
import hashlib
import time

with open('config.json', 'r') as config_file:
    data = config_file.read()
config = json.loads(data)

def test_slack_sig(request):
    """Verify Slack Signature against Signing Secret"""
    timestamp = request.headers['X-Slack-Request-Timestamp']
    if int(time.time()) - int(timestamp) > 60*5:
        return False

    slack_signing_secret = config['SLACK_SIGNING_SECRET']
    slack_signature = request.headers['X-Slack-Signature']
    request_body = request.get_data(as_text=True)
    sig_basestring = 'v0:' + timestamp + ':' + request_body
    hmac_obj = hmac.new(slack_signing_secret.encode(), sig_basestring.encode(), hashlib.sha256)
    calc_signature = 'v0=' + hmac_obj.hexdigest()

    return hmac.compare_digest(calc_signature, slack_signature)

def kg_query(query):
    """Query Google Knowledge Graph API."""
    api_key = config['API_KEY']
    kg_url = 'https://kgsearch.googleapis.com/v1/entities:search'

    params = {'query':query, 'key':api_key, 'limit':'1', 'indent':'True'}
    kg_response = requests.get(kg_url, params)

    return kg_response

def format_message(response):
    """Format Slack message."""
    message_text = response.json()['itemListElement'][0]['result']['description']
    message_image_url = response.json()['itemListElement'][0]['result']['image']['contentUrl']
    message = {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message_text
                                }
                    },
                    {
                        "type": "image",
                        "image_url": message_image_url,
                        "alt_text": message_text
                    }
                        ]
            }
    return message

def kg_query_to_slack(request):
    """Main func."""
    if not test_slack_sig(request):
        return jsonify({"response_type": "in_channel", "text":"Invalid Sig"})
    query = request.form['text']
    response = kg_query(query)
    message = format_message(response)

    return jsonify(message)
