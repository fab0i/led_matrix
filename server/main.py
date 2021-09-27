from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok

from RgbMatrix import RgbMatrix
import time
import sys

app = Flask(__name__)
run_with_ngrok(app)

matrix = RgbMatrix(32, 32)

@app.route('/', methods=['GET', 'POST'])
def add_message():
    json_data = request.json
    print(request)
    print(json_data)
    action = json_data['action']
    image = json_data['img']

    if action == 'render_gif':
        matrix.render_gif(image, 10)

    return jsonify({'status': 200})

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)