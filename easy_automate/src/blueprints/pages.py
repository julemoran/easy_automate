from flask import Blueprint, request, jsonify
from .. import db
from ..models import Page, Application

bp = Blueprint('pages', __name__)

@bp.route('', methods=['POST'])
def create_page():
    data = request.get_json() or {}

    required_fields = ['name', 'application_id', 'identifying_selectors']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if not Application.query.get(data['application_id']):
        return jsonify({'error': 'Application not found'}), 404

    page = Page(
        name=data['name'],
        application_id=data['application_id'],
        url=data.get('url'),
        can_be_navigated_to=data.get('can_be_navigated_to', False),
        identifying_selectors=data['identifying_selectors'],
        interactive_selectors=data.get('interactive_selectors', [])
    )

    db.session.add(page)
    db.session.commit()

    return jsonify(page.to_dict()), 201

@bp.route('', methods=['GET'])
def get_pages():
    pages = Page.query.all()
    return jsonify([page.to_dict() for page in pages])

@bp.route('/<int:id>', methods=['GET'])
def get_page(id):
    page = Page.query.get_or_404(id)
    return jsonify(page.to_dict())

@bp.route('/<int:id>', methods=['PUT'])
def update_page(id):
    page = Page.query.get_or_404(id)
    data = request.get_json() or {}

    page.name = data.get('name', page.name)
    page.url = data.get('url', page.url)
    page.can_be_navigated_to = data.get('can_be_navigated_to', page.can_be_navigated_to)
    page.identifying_selectors = data.get('identifying_selectors', page.identifying_selectors)
    page.interactive_selectors = data.get('interactive_selectors', page.interactive_selectors)

    db.session.commit()
    return jsonify(page.to_dict())

@bp.route('/<int:id>', methods=['DELETE'])
def delete_page(id):
    page = Page.query.get_or_404(id)
    db.session.delete(page)
    db.session.commit()
    return '', 204