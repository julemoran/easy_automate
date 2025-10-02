from flask import Blueprint, request, jsonify
from .. import db
from ..models import Application

bp = Blueprint('applications', __name__)

@bp.route('', methods=['POST'])
def create_application():
    data = request.get_json() or {}
    if 'name' not in data:
        return jsonify({'error': 'Missing name'}), 400
    if Application.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Application with this name already exists'}), 400

    app = Application(name=data['name'])
    db.session.add(app)
    db.session.commit()

    return jsonify(app.to_dict()), 201

@bp.route('', methods=['GET'])
def get_applications():
    apps = Application.query.all()
    return jsonify([app.to_dict() for app in apps])

@bp.route('/<int:id>', methods=['GET'])
def get_application(id):
    app = Application.query.get_or_404(id)
    return jsonify(app.to_dict())

@bp.route('/<int:id>', methods=['PUT'])
def update_application(id):
    app = Application.query.get_or_404(id)
    data = request.get_json() or {}

    if 'name' in data:
        if Application.query.filter(Application.name == data['name'], Application.id != id).first():
            return jsonify({'error': 'Application with this name already exists'}), 400
        app.name = data['name']

    db.session.commit()
    return jsonify(app.to_dict())

@bp.route('/<int:id>', methods=['DELETE'])
def delete_application(id):
    app = Application.query.get_or_404(id)
    db.session.delete(app)
    db.session.commit()
    return '', 204