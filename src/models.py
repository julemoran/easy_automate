from src import db

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    pages = db.relationship('Page', backref='application', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    url = db.Column(db.String(256))
    can_be_navigated_to = db.Column(db.Boolean, default=False)
    identifying_selectors = db.Column(db.JSON, nullable=False)  # List of {'alias': '...', 'xpath': '...', 'visible': true/false (optional)}
    interactive_selectors = db.Column(db.JSON)   # List of {'alias': '...', 'xpath': '...', 'visible': true/false (optional)}

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'application_id': self.application_id,
            'url': self.url,
            'can_be_navigated_to': self.can_be_navigated_to,
            'identifying_selectors': self.identifying_selectors,
            'interactive_selectors': self.interactive_selectors
        }