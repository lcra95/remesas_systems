from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import sys
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://lrequena:18594LCra..@170.239.85.238/delivery'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route('/')
def home():
    return ":)"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5353, debug=True)
