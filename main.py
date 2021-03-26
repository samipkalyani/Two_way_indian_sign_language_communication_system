from flask import Flask, render_template, request, abort
import os
from dotenv import load_dotenv
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant, ChatGrant
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import build
import predict
login=True

load_dotenv()
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_api_key_sid = os.environ.get('TWILIO_API_KEY_SID')
twilio_api_key_secret = os.environ.get('TWILIO_API_KEY_SECRET')
twilio_client = Client(twilio_api_key_sid, twilio_api_key_secret,twilio_account_sid)
app=Flask(__name__)


def get_chatroom(name):
    global login
    for conversation in twilio_client.conversations.conversations.list():
        if conversation.friendly_name == name and login:
            twilio_client.conversations.conversations(conversation.sid).delete()
            login=False
            return twilio_client.conversations.conversations.create(friendly_name=name)
        if conversation.friendly_name == name and not login:
            return conversation

    # a conversation with the given name does not exist ==> create a new one
    return twilio_client.conversations.conversations.create(
        friendly_name=name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.get_json(force=True).get('username')
    if not username:
        abort(401)

    conversation = get_chatroom('My Room')
    try:
        conversation.participants.create(identity=username)
    except TwilioRestException as exc:
        # do not error if the user is already in the conversation
        if exc.status != 409:
            raise

    token = AccessToken(twilio_account_sid, twilio_api_key_sid,
                        twilio_api_key_secret, identity=username)
    token.add_grant(VideoGrant(room='My Room'))
    token.add_grant(ChatGrant(service_sid=conversation.chat_service_sid))

    return {'token': token.to_jwt().decode(),
            'conversation_sid': conversation.sid}

@app.route('/recognition',methods=['POST'])
def recognition():
    b = build.main('./protected/test/','./output/')
    b.build()
    p = predict.main('./output/Absolute/')
    word = p.pred()
    print(word)
    return {'status': 200,'word': word}
    

if __name__ == '__main__':
    app.run(host='0.0.0.0')
