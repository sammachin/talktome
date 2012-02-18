import cherrypy
from twilio import twiml
from twilio.rest import TwilioRestClient
import urllib
import urllib2
import json
import memcache

settings.configure(TEMPLATE_DIRS = ( "/server/talktome/static",))

mc = memcache.Client(['127.0.0.1:11211'], debug=0)

# Twilio Credentials
account = "xxx"
token = "xxx"

#Pearson Credentials
apikey = "xxx"


def getword(word):
	baseurl = 'https://api.pearson.com/longman/dictionary'
	requrl = baseurl + "/entry.json?q=" + word +"&apikey=" + apikey
	resp = urllib2.urlopen(requrl)
	respData = resp.read()
	responseJSON = json.loads(respData)
	for x in responseJSON['Entries']['Entry']['multimedia']:
		if x['@type'] == "GB_PRON":
			soundurl = baseurl + x['@href'] + "?apikey=" + apikey
	return soundurl
	
	
class start(object):
	create = create()
	def index(self):
		template_values = {}
		t = loader.get_template('home.html')
		c = Context(template_values)
		return t.render(c)
	def sms(self, var=None, **params):
		msg = urllib.unquote(cherrypy.request.params['Body'])
		cli = urllib.unquote(cherrypy.request.params['From']).lstrip("+")
		phrase = []
		for word in msg.split(" "):
			url = getword(word)
			phrase.append(url)
		mc.set(cli, phrase, 180)
		print phrase
		client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
		call = client.calls.create(to=cli, from_="xxx", url="http://foo.com/talktome/call")
		return "ok"
	def call(self, var=None, **params):
		cli = urllib.unquote(cherrypy.request.params['From']).lstrip("+")
		phrase = mc.get(str(cli))
		r = twiml.Response()
		for url in phrase:
			r.play(url)
		return str(r)
	call.exposed = True
	sms.exposed = True
	index.exposed = True
	

cherrypy.config.update('app.cfg')
app = cherrypy.tree.mount(start(), '/', 'app.cfg')
cherrypy.config.update({'server.socket_host': ip,
                        'server.socket_port': port})

if hasattr(cherrypy.engine, "signal_handler"):
    cherrypy.engine.signal_handler.subscribe()
if hasattr(cherrypy.engine, "console_control_handler"):
    cherrypy.engine.console_control_handler.subscribe()
cherrypy.engine.start()
cherrypy.engine.block()

