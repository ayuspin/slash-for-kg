import requests
import json
from flask import jsonify

from unittest.mock import Mock
from flask import Flask

def kg_query(request):

    with open('config.json', 'r') as config_file:
        data = config_file.read()

    api_key = json.loads(data)['API_KEY']
    kg_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    query = request.form['text']
    params = {'query':query, 'key':api_key, 'limit':'1', 'indent':'True'}
    response = requests.get(kg_url, params)

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

    app = Flask(__name__)
    with app.app_context():
        print(jsonify(message))

if __name__ == '__main__':
    request = Mock ()
    request.form = {'text':'zeebra'}
    kg_query(request)
