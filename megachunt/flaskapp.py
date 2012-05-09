from flask import Flask
import settings

app = Flask('megachunt')
app.config.from_object('settings')
