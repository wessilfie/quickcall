# flask and twilio libraries
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.voice_response import Play, VoiceResponse, Say
from twilio.twiml.messaging_response import MessagingResponse

#spotify libraries
import spotipy
import spotipy.oauth2 as oauth2

# remaining libraries
import random
import urllib

credentials = oauth2.SpotifyClientCredentials(
		client_id='SPOTIFY_CLIENT_ID',
		client_secret='SPOTIFY_CLIENT_SECRET')

account_sid = "TWILIO_ACCOUNT_SID"
auth_token = "TWILIO_AUTH_TOKEN"
client = Client(account_sid, auth_token)

#placeholder values, will be replaced
NGROK_URL = "PROGRAM_NGROK_URL"
PHONE_NUMBER = "+12345678912"

app = Flask(__name__)

@app.route("/song/<track>", methods=['GET', 'POST'])
def xml_song(track):
	# returns TwiML that is a song to be played to the user
    return "<?xml version=\"1.0\" encoding=\"UTF-8\"?> <Response> \
    <Play>" + get_song(track) + "</Play></Response>"

@app.route("/call", methods=['GET', 'POST'])
def make_call(sender,song_name):
	#extract song name from the data provided
	song_name = urllib.parse.quote(song_name)

	# uses the /song/<track> dynamic endpoint to generate Twilio XML for generating a call
	call_url = NGROK_URL + "/song/" + song_name
	
	# call the user with the call url 
	call = client.calls.create(
    to=sender,
    from_=PHONE_NUMBER,
    url=call_url
	)
	return "done"

def get_song(song_name):
	# initialize spotify API and search for a song given what the user texted 
	token = credentials.get_access_token()
	sp = spotipy.Spotify(auth=token)
	results = sp.search(q=song_name, limit=4, type='track')
	#try to get a song result based off what the user texted
	try:
		song_preview = results['tracks']['items'][0]['preview_url']
		print(song_preview)
	# return a default song if nothing can be found based off user search
	except:
		song_preview = "https://p.scdn.co/mp3-preview/bff3df4e9db9504832d3c5d29a30e2b10b1acd19?cid=dd6f7c91ebbd4d379e12511f4bd2a181"
	if song_preview is None:
		song_preview = "https://p.scdn.co/mp3-preview/bff3df4e9db9504832d3c5d29a30e2b10b1acd19?cid=dd6f7c91ebbd4d379e12511f4bd2a181"

	# return a song link that will be played to the user
	return song_preview



@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    # Randomly select a message response to send back to the user 
    response_list = ["Great to hear from you! Actually, hold on need to call you.", "Hey! Can you call me back?", "I have a question -- calling now"]

    #Use Twilio library to process the text message received to the endpoint
    resp = MessagingResponse()
    resp.message(random.choice(response_list))
    # Extract the text of what the user sent. If no text, defaults to Bodak Yellow
    body = request.values.get('Body', 'Happy')
    # Gets the sender’s number. Defaults to None if no sender found.
    sender = request.values.get('From', None)

    try:
    	make_call(sender, body)
    except:
    	print("error")
    	return -1

    #return message response (the text) to the user.
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
