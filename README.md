# ChatOne
Chat app for Android (can be cross-platform) using Python, Kivy, Pusher, and Firebase 

Chat app is ready but in its early stages.

Inside app you can find dictinary with avaible users - you can expand it to use with your nicknames.

In order to use you should create auth_key.json file which should include all security-related data, such as PUSHER_APP_KEY etc
you can see it on the top of main.py file.

To build it to your Android device you will need Buildozer to be installed so you can build an APK (probably you will run in some troubles with Pusher import - you can easily overcome them if you follow exceptions trail (maybe I will include fixed Pysher module in a future).
