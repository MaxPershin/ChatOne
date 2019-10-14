from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader

import requests
from pusher import Pusher
import pysher

import os
import json
import threading
from datetime import datetime

Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '414')
Config.set('graphics', 'height', '736')

with open("auth_key.json", "r") as f:
    keys = json.load(f)

auth_key = keys['auth_key']
url = keys['url']

PUSHER_APP_ID = keys['PUSHER_APP_ID']
PUSHER_APP_KEY = keys['PUSHER_APP_KEY']
PUSHER_APP_SECRET = keys['PUSHER_APP_SECRET']
PUSHER_APP_CLUSTER = keys['PUSHER_APP_CLUSTER']


class ChatApp(App):
    app_opened = True
    pusher = None
    channel = None
    chatroom = None
    clientPusher = None
    user = None
    users = {"max": "1",
             "max2": '1',
             "sovilaz": "1"}
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
            self.pusher.trigger(self.chatroom, u'newmessage', {'user': self.user, 'message': message})

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
        self.pusher = Pusher(app_id=PUSHER_APP_ID, key=PUSHER_APP_KEY, secret=PUSHER_APP_SECRET,
                             cluster=PUSHER_APP_CLUSTER)
        self.clientPusher = pysher.Pusher(PUSHER_APP_KEY, PUSHER_APP_CLUSTER)
        self.clientPusher.connection.bind('pusher:connection_established', self.connectHandler)
        self.clientPusher.connect()

    def connectHandler(self, data):
        self.channel = self.clientPusher.subscribe(self.chatroom)
        self.channel.bind('newmessage', self.pusherCallback)
        # saying hi to chatroom
        message = '$im_in$'
        self.pusher.trigger(self.chatroom, u'newmessage', {'user': self.user, 'message': message})

    def pusherCallback(self, message):
        message = json.loads(message)

        # check if it is a service message
        if message['user'] == self.user:
            if message['message'] == '$im_in$' or message['message'] == '$im_out$' or message['message'] == '$me_too$':
                return
        else:
            if message['message'] == '$im_in$':
                message = '[size=20sp][b][color=A9A9A9]Пользователь {} вошел в сеть[/color][/b][/size]'.format(
                    message['user'])
                self.root.ids.chat_logs.text += message + '\n'
                self.friend = True
                message = '$me_too$'
                self.pusher.trigger(self.chatroom, u'newmessage', {'user': self.user, 'message': message})
                return
            if message['message'] == '$im_out$':
                message = '[size=20sp][b][color=A9A9A9]Пользователь {} вышел из сети[/color][/b][/size]'.format(
                    message['user'])
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

    def outsender(self):
        message = self.root.ids.message.text
        try:
            self.pusher.trigger(self.chatroom, u'newmessage', {'user': self.user, 'message': message})
        except:
            self.popup('Sorry', 'No internet connection')
        self.root.ids.message.text = ''

    def send_msg(self):
        my_thread = threading.Thread(target=self.outsender)
        my_thread.start()

    def focus(self, out):
        if os.name != 'posix':
            if out.focus:
                self.root.ids.chatroom.pos_hint = {"center_x": .5, "center_y": .87}
            else:
                self.root.ids.chatroom.pos_hint = {"center_x": .5, "center_y": .5}

    def popup(self, title, text):
        popup = Popup(title=title,
                      content=Label(text=text),
                      size_hint=(0.65, 0.25))
        popup.open()


if __name__ == '__main__':
    ChatApp().run()
