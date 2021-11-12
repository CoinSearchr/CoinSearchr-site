from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

app.url_map.strict_slashes = False

# silly testing page to ensure the server is technically working
@app.route('/test')
def test():
	return 'Hello World'

# must go at bottom
from . import views # not accessed, required
