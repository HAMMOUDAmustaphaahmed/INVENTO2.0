from flask import Blueprint, jsonify, render_template

blueprint = Blueprint('main', __name__)

@blueprint.route('/')
def index():
    return render_template('index.html')
