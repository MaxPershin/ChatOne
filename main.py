from kivy.app import App
from kivy.config import Config
import json
import requests
from kivy.clock import Clock
import threading
from kivy.uix.popup import Popup
from kivy.uix.label import Label

Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '414')
Config.set('graphics', 'height', '736')

auth_key = '45uG9hhwkc6A5EQcyxtlxGMzWlHlbzZnopejiwxK'
url = 'https://chatone-39de9.firebaseio.com/.json'

class ChatApp(App):

	def build(self):
		return 

	def pull_chat(self):
		if self.root.ids.nickname.text == '':
			self.popup('Sorry', 'Type your name!')
			return
		self.onliner = False
		try:
			self.root.current = 'chatroom'
			self.nickname = self.root.ids.nickname.text
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

	def mult_thread(self):
		self.send_msg()
		self.check_if_sent(self.previous_mgs)


	def easy_send_msg(self, *args):
		glob_thread = threading.Thread(target=self.mult_thread)
		glob_thread.start()

	def check_if_sent(self, msg):
		try:
			request = requests.get(url + "?auth=" + auth_key)
			anwser = request.json()
		except:
			self.popup('Sorry', 'No internet connection')
			return

		self.glob = anwser

		if msg.replace('"', "@#dq").replace('$', "@#dol").replace('\\', '@#esc').replace('\n', '@#nl') not in self.glob['source']:
			self.temp = self.glob['source']
			self.temp += self.nickname + ": " + msg + '$'
			self.glob['source'] = self.temp

			sender = '{' + '"source":' + ' "{}"'.format(self.glob['source']) + '}'
			to_database = json.loads(sender)
			try:
				requests.patch(url=url, json=to_database)
			except:
				self.popup('Sorry', 'No internet connection')
				return

			self.root.ids.message.text = ''
			self.pull_single()
			self.easy_refresh()

	def send_msg(self):
			self.previous_mgs = self.root.ids.message.text

			try:
				request = requests.get(url + "?auth=" + auth_key)
				anwser = request.json()
			except:
				self.popup('Sorry', 'No internet connection')
				return

			self.glob = anwser

			self.temp = self.glob['source']
			self.temp += self.nickname + ": " + self.root.ids.message.text.replace('"', "@#dq").replace('$', "@#dol").replace('\\', '@#esc').replace('\n', '@#nl') + '$'
			self.glob['source'] = self.temp
			sender = '{' + '"source":' + ' "{}"'.format(self.temp) + '}'

			to_database = json.loads(sender)

			try:
				requests.patch(url=url, json=to_database)
			except:
				self.popup('Sorry', 'No internet connection')
				return

			self.root.ids.message.text = ''
			self.pull_single()

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

	def disconnect(self):
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

	def online(self):
		if self.onliner == False:
			self.onliner = True
			self.root.ids.online_button.text = 'online ON'
			Clock.schedule_interval(self.easy_refresh, 5)
		else:
			self.root.ids.online_button.text = 'online OFF'
			self.onliner = False
			Clock.unschedule(self.easy_refresh)

	def popup(self, title, text):
		popup = Popup(title=title,
		content=Label(text=text),
		size_hint=(0.65, 0.25))
		popup.open()

if __name__ == '__main__':
	ChatApp().run()