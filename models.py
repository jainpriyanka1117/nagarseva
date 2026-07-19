from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Ward(db.Model):
    """Represents a ward/administrative division."""
    __tablename__ = 'ward'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    
    # Relationships
    complaints = db.relationship('Complaint', backref='ward', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ward {self.name}>'


class Authority(db.Model):
    """Represents an authority/department that handles complaints."""
    __tablename__ = 'authority'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    handles = db.Column(db.Text, nullable=False)  # Comma-separated category list
    
    # Relationships
    complaints = db.relationship('Complaint', backref='authority', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Authority {self.name}>'
    
    def get_categories(self):
        """Returns list of categories this authority handles."""
        return [cat.strip() for cat in self.handles.split(',')]
    
    def set_categories(self, categories):
        """Set categories from a list."""
        self.handles = ','.join(categories)


class Complaint(db.Model):
    """Represents a complaint/issue reported by a user."""
    __tablename__ = 'complaint'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    severity = db.Column(
        db.String(20),
        nullable=False,
        default='routine',
        comment='routine or life_threatening'
    )
    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending',
        comment='pending, in_progress, or resolved'
    )
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo_path = db.Column(db.String(500), nullable=True)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'), nullable=False)
    authority_id = db.Column(db.Integer, db.ForeignKey('authority.id'), nullable=False)
    confirm_count = db.Column(db.Integer, default=1, nullable=False)
    anonymous = db.Column(db.Boolean, default=False, nullable=False)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resolved_photo_path = db.Column(db.String(500), nullable=True)
    
    # Relationships
    status_history = db.relationship(
        'StatusHistory',
        backref='complaint',
        lazy=True,
        cascade='all, delete-orphan',
        order_by='StatusHistory.timestamp'
    )
    
    def __repr__(self):
        return f'<Complaint {self.id} - {self.category}>'


class StatusHistory(db.Model):
    """Records the history of status changes for a complaint."""
    __tablename__ = 'status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    status = db.Column(
        db.String(20),
        nullable=False,
        comment='pending, in_progress, or resolved'
    )
    note = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<StatusHistory complaint_id={self.complaint_id} status={self.status}>'


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
