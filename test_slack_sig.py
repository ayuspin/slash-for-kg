from flask import Flask, request
import hmac
import hashlib
from flask_ngrok import run_with_ngrok

with open('config.json', 'r') as config_file:
    data = config_file.read()
config = json.loads(data)

app = Flask(__name__)
#run_with_ngrok(app)

@app.route("/", methods=['POST'])
def print_request_info():

    slack_signing_secret = config['SLACK_SIGNING_SECRET']
    slack_signature = request.headers['X-Slack-Signature']
    timestamp = request.headers['X-Slack-Request-Timestamp']
    request_body = request.get_data(as_text=True)
    sig_basestring = 'v0:' + timestamp + ':' + request_body

    hmac_obj = hmac.new(slack_signing_secret.encode(), sig_basestring.encode(), hashlib.sha256)
    calc_signature = 'v0=' + hmac_obj.hexdigest()

    return '''
    Sig base string: {}
    Calculated Signature: {}
    Slack Signature: {}

    '''.format(sig_basestring, str(calc_signature), slack_signature)

if __name__ == '__main__':
    app.run()
