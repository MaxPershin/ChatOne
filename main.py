from kivy.app import App
from kivy.config import Config
import json
from pusher import Pusher
import pysher
import requests
from kivy.clock import Clock
import threading
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from datetime import datetime
from kivy.core.audio import SoundLoader

Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '414')
Config.set('graphics', 'height', '736')


auth_key = '45uG9hhwkc6A5EQcyxtlxGMzWlHlbzZnopejiwxK'
url = 'https://chatone-39de9.firebaseio.com/.json'

PUSHER_APP_ID='853308'
PUSHER_APP_KEY='a7d3caa6f11e8e40b649'
PUSHER_APP_SECRET='9618775036978ef089a7'
PUSHER_APP_CLUSTER='eu'

class ChatApp(App):

	app_opened = True
	pusher = None
	channel = None
	chatroom = None
	clientPusher = None
	user = None
	users = {"max": "1",
			"max2":'1',
			"sovilaz": "1"}
	chatrooms = ["general"]
	sound_msg = SoundLoader.load('src/h.wav')
	friend = False

	def on_pause(self):
		self.app_opened = False
		return True

	def on_resume(self):
		self.app_opened = True
		return True

	def on_stop(self):
		if self.channel:
			message = '$im_out$'
			self.pusher.trigger(self.chatroom, u'newmessage', {'user':self.user, 'message': message})
		
		print('I know I have to stop bruh')
		return True

	def build(self):
		return 

	def login(self):
		if self.root.ids.nickname.text == '':
			self.popup('Sorry', 'Type your name!')
			return

		username = self.root.ids.nickname.text

		if username in self.users:
			self.user = username
		else:
			self.popup('Sorry', 'No such user')
			return

		self.chatroom = 'general'

		self.initPusher()

		self.root.current = 'chatroom'

	def initPusher(self):
		self.pusher = Pusher(app_id=PUSHER_APP_ID, key=PUSHER_APP_KEY, secret=PUSHER_APP_SECRET, cluster=PUSHER_APP_CLUSTER)
		self.clientPusher = pysher.Pusher(PUSHER_APP_KEY, PUSHER_APP_CLUSTER)
		self.clientPusher.connection.bind('pusher:connection_established', self.connectHandler)
		self.clientPusher.connect()

	def connectHandler(self, data):
		self.channel = self.clientPusher.subscribe(self.chatroom)
		self.channel.bind('newmessage', self.pusherCallback)
		#saying hi to chatroom
		message = '$im_in$'
		self.pusher.trigger(self.chatroom, u'newmessage', {'user':self.user, 'message': message})

	def pusherCallback(self, message):
		message = json.loads(message)

		#check if it is a service message
		if message['user'] == self.user:
			if message['message'] == '$im_in$' or message['message'] == '$im_out$' or message['message'] == '$me_too$':
				return
		else:
			if message['message'] == '$im_in$':
				message = '[size=20sp][b][color=A9A9A9]Пользователь {} вошел в сеть[/color][/b][/size]'.format(message['user'])
				self.root.ids.chat_logs.text += message + '\n'
				self.friend = True
				message = '$me_too$'
				self.pusher.trigger(self.chatroom, u'newmessage', {'user':self.user, 'message': message})
				return
			if message['message'] == '$im_out$':
				message = '[size=20sp][b][color=A9A9A9]Пользователь {} вышел из сети[/color][/b][/size]'.format(message['user'])
				self.root.ids.chat_logs.text += message + '\n'
				self.friend = False
				return
			if message['message'] == '$me_too$':
				message = '[size=20sp][b][color=A9A9A9]Ваш собеседник в сети[/color][/b][/size]'
				self.root.ids.chat_logs.text += message + '\n'
				self.friend = True
				return


		if message['user'] != self.user:
			message = '[b][color=2980B9]{}:[/color][/b] {}'.format(message['user'], message['message'])
			self.root.ids.chat_logs.text += message + '\n'
			if self.app_opened:
				try:
					self.sound_msg.play()
				except:
					pass
			
		else:
			message = '[b][color=27db9f]{}:[/color][/b] {}'.format(message['user'], message['message'])
			self.root.ids.chat_logs.text += message + '\n'
			

	#old-style loading
	#def pull_chat(self):
		'''try:
			self.root.current = 'chatroom'
			request = requests.get(url + "?auth=" + auth_key)
			anwser = request.json()
			self.glob = anwser
			whole_chat = anwser['source']
			whole_chat = whole_chat.split('$')[:-1]
			for each in whole_chat:
				name, msg = each.split(':', 1)
				if name != self.nickname:
					each = ('[b][color=2980B9]{}:[/color][/b] {}'.format(name, msg.replace('@#dq', '"').replace("@#dol", '$').replace('@#esc', '\\').replace('@#nl', '\n')))
				else:
					each = ('[b][color=27db9f]{}:[/color][/b][/b] {}'.format(name, msg.replace('@#dq', '"').replace("@#dol", '$').replace('@#esc', '\\').replace('@#nl', '\n')))

				self.root.ids.chat_logs.text += each + '\n'
			
		except:
			self.popup('Sorry', 'No internet')
'''

	def outsender(self):
		message = self.root.ids.message.text
		try:
			self.pusher.trigger(self.chatroom, u'newmessage', {'user':self.user, 'message': message})
		except:
			self.popup('Sorry', 'No internet connection')
		self.root.ids.message.text = ''

	def send_msg(self):
		my_thread = threading.Thread(target=self.outsender)
		my_thread.start()

	def pull_single(self):
		try:
			whole_chat = self.glob['source']
			whole_chat = whole_chat.split('$')[:-1]
			sent = whole_chat[-1]
			name, msg = sent.split(':', 1)
			each = ('[b][color=27db9f]{}:[/color][/b][/b] {}'.format(name, msg.replace('@#dq', '"').replace("@#dol", '$').replace('@#esc', '\\').replace('@#nl', '\n')))

			self.root.ids.chat_logs.text += each + '\n'
			
		except Exception as e:
			self.popup('Sorry', 'Some errors has occured!')

	def disconnect(self, data):
		data.text = '[color=#000000]I[/color]'
		sender = '{' + '"source":' + ' ""' + '}'
		to_database = json.loads(sender)
		try:
			requests.patch(url=url, json=to_database)
		except:
			self.popup('Sorry', 'No internet connection')
			return

		self.root.ids.chat_logs.text = ''

	def refresh(self):
		try:
			request = requests.get(url + "?auth=" + auth_key)
			anwser = request.json()
			self.glob = anwser
			whole_chat = anwser['source']
			whole_chat = whole_chat.split('$')[:-1]
			self.root.ids.chat_logs.text = ''
			for each in whole_chat:
				name, msg = each.split(':', 1)
				if name != self.nickname:
					each = ('[b][color=2980B9]{}:[/color][/b] {}'.format(name, msg.replace('@#dq', '"').replace("@#dol", '$').replace('@#esc', '\\').replace('@#nl', '\n')))
				else:
					each = ('[b][color=27db9f]{}:[/color][/b][/b] {}'.format(name, msg.replace('@#dq', '"').replace("@#dol", '$').replace('@#esc', '\\').replace('@#nl', '\n')))

				self.root.ids.chat_logs.text += each + '\n'
			
		except Exception as e:
			self.popup('Sorry', 'Some errors has occured!')

	def focus(self, out):
		if(out.focus):
			self.root.ids.chatroom.pos_hint = {"center_x": .5,"center_y": .87}
		else:
			self.root.ids.chatroom.pos_hint = {"center_x": .5,"center_y": .5}

	def easy_refresh(self, *args):

		my_thread = threading.Thread(target=self.refresh)
		my_thread.start()

	def color(self, data):
		data.text = '[color=#009ddf]I[/color]'

	def color2(self, data):
		data.text = '[color=#009ddf]R[/color]'

	def color3(self, data):
		data.text = '[color=#000000]R[/color]'

	def online(self):
		if self.onliner == False:
			self.onliner = True
			self.root.ids.online_button.text = '[color=#009ddf]w[/color]'
			Clock.schedule_interval(self.easy_refresh, 5)
		else:
			self.root.ids.online_button.text = '[color=#000000]w[/color]'
			self.onliner = False
			Clock.unschedule(self.easy_refresh)

	def popup(self, title, text):
		popup = Popup(title=title,
		content=Label(text=text),
		size_hint=(0.65, 0.25))
		popup.open()

if __name__ == '__main__':
	ChatApp().run()
