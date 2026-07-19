"""
Flask Complaint Reporting API
Handles complaint creation, listing, confirmation, and status tracking with duplicate detection.
"""

import math
import os
from datetime import datetime
from flask import Flask, request, jsonify
from models import db, init_db, Ward, Authority, Complaint, StatusHistory
from seed import seed_database


# ============================================================================
# Haversine Distance Function
# ============================================================================

def haversine_distance(lat1, lng1, lat2, lng2):
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1, lng1: First point coordinates (latitude, longitude in degrees)
        lat2, lng2: Second point coordinates (latitude, longitude in degrees)
    
    Returns:
        Distance in meters
    """
    R = 6371000  # Earth's radius in meters
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c
    return distance


# ============================================================================
# Category-Specific Radius Configuration
# ============================================================================

DUPLICATE_CHECK_RADIUS = {
    'pothole': 15,
    'garbage': 20,
    'exposed_wire': 25,
    'streetlight': 15,
    'blocked_drain': 20,
    'unsafe_area': 25,
    'encroachment': 15,
    'waterlogging': 20,
    'road_damage': 15,
    'illegal_dumping': 20,
}


# ============================================================================
# Flask App Initialization
# ============================================================================

app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "complaints.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False




# ============================================================================
# Helper Functions
# ============================================================================

def complaint_to_dict(complaint):
    """
    Convert a Complaint model instance to a dictionary for JSON serialization.
    
    Args:
        complaint: Complaint model instance
    
    Returns:
        Dictionary representation of complaint
    """
    return {
        'id': complaint.id,
        'category': complaint.category,
        'severity': complaint.severity,
        'status': complaint.status,
        'lat': complaint.lat,
        'lng': complaint.lng,
        'description': complaint.description,
        'photo_path': complaint.photo_path,
        'ward_id': complaint.ward_id,
        'authority_id': complaint.authority_id,
        'confirm_count': complaint.confirm_count,
        'anonymous': complaint.anonymous,
        'reported_at': complaint.reported_at.isoformat() if complaint.reported_at else None,
        'resolved_photo_path': complaint.resolved_photo_path,
    }


def find_duplicate_complaint(category, lat, lng, ward_id):
    """
    Search for existing complaints of the same category within the category-specific radius.
    
    Args:
        category: Complaint category
        lat, lng: Latitude and longitude of new complaint
        ward_id: Ward ID (filter to same ward)
    
    Returns:
        Complaint instance if found, None otherwise
    """
    radius_meters = DUPLICATE_CHECK_RADIUS.get(category, 20)
    
    # Find all complaints of the same category in the same ward with status 'pending' or 'in_progress'
    existing_complaints = Complaint.query.filter_by(
        category=category,
        ward_id=ward_id
    ).filter(Complaint.status.in_(['pending', 'in_progress'])).all()
    
    for complaint in existing_complaints:
        distance = haversine_distance(lat, lng, complaint.lat, complaint.lng)
        if distance <= radius_meters:
            return complaint
    
    return None


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200


@app.route('/api/complaints', methods=['POST'])
def create_complaint():
    """
    Create a new complaint or return a possible duplicate.
    
    Expected JSON:
    {
        "category": "pothole",
        "description": "Large pothole on main street",
        "lat": 19.1364,
        "lng": 72.8296,
        "ward_id": 1,
        "photo": "path/to/photo.jpg",  # REQUIRED
        "severity": "routine",  # Optional, defaults to 'routine'
        "anonymous": false  # Optional, defaults to false
    }
    
    Returns:
        - If duplicate found: 200 with 'possible_duplicate' and existing complaint data
        - If new complaint created: 201 with new complaint data
        - If error: 400 with error message
    """
    data = request.get_json()
    
    # Validate required fields (including photo)
    required_fields = ['category', 'description', 'lat', 'lng', 'ward_id', 'photo']
    if not data or not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'required': required_fields
        }), 400
    
    # Validate photo is not empty
    if not data.get('photo'):
        return jsonify({
            'error': 'Photo cannot be empty'
        }), 400
    
    category = data.get('category')
    description = data.get('description')
    lat = data.get('lat')
    lng = data.get('lng')
    ward_id = data.get('ward_id')
    photo = data.get('photo')
    severity = data.get('severity', 'routine')
    anonymous = data.get('anonymous', False)
    # Validate ward exists
    ward = Ward.query.get(ward_id)
    if not ward:
        return jsonify({'error': f'Ward {ward_id} not found'}), 400
    
    # Find authority that handles this category
    authority = Authority.query.filter(
        Authority.handles.contains(category)
    ).first()
    
    if not authority:
        return jsonify({
            'error': f'No authority found to handle category: {category}'
        }), 400
    
    # Check for duplicate
    duplicate = find_duplicate_complaint(category, lat, lng, ward_id)
    if duplicate:
        return jsonify({
            'result': 'possible_duplicate',
            'complaint': complaint_to_dict(duplicate)
        }), 200
    
    # Create new complaint
    new_complaint = Complaint(
        category=category,
        description=description,
        lat=lat,
        lng=lng,
        ward_id=ward_id,
        authority_id=authority.id,
        photo_path=photo,
        severity=severity,
        anonymous=anonymous,
        confirm_count=1,
        reported_at=datetime.utcnow(),
        status='pending'
    )
    
    db.session.add(new_complaint)
    db.session.commit()
    
    # Log initial status to history
    status_record = StatusHistory(
        complaint_id=new_complaint.id,
        status='pending',
        note='Complaint created'
    )
    db.session.add(status_record)
    db.session.commit()
    
    return jsonify({
        'result': 'created',
        'complaint': complaint_to_dict(new_complaint)
    }), 201

@app.route('/api/complaints/<int:complaint_id>/confirm', methods=['POST'])
def confirm_complaint(complaint_id):
    """
    Increment the confirm_count for an existing complaint.
    
    This endpoint is called when a user confirms/upvotes an existing complaint.
    
    Returns:
        - 200 with updated complaint data if successful
        - 404 if complaint not found
    """
    complaint = Complaint.query.get(complaint_id)
    
    if not complaint:
        return jsonify({'error': f'Complaint {complaint_id} not found'}), 404
    
    complaint.confirm_count += 1
    db.session.commit()
    
    return jsonify({
        'message': 'Complaint confirmed',
        'complaint': complaint_to_dict(complaint)
    }), 200


@app.route('/api/complaints', methods=['GET'])
def list_complaints():
    """
    List complaints with optional filters.
    
    Query Parameters:
        - status: Filter by status (pending, in_progress, resolved)
        - category: Filter by category
        - ward_id: Filter by ward ID
        - severity: Filter by severity (routine, life_threatening)
        - limit: Number of results to return (default 50)
        - offset: Number of results to skip (default 0)
    
    Returns:
        - 200 with list of complaints and total count
    """
    # Get query parameters
    status = request.args.get('status')
    category = request.args.get('category')
    ward_id = request.args.get('ward_id')
    severity = request.args.get('severity')
    limit = request.args.get('limit', default=50, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    # Start building query
    query = Complaint.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    if ward_id:
        query = query.filter_by(ward_id=ward_id)
    if severity:
        query = query.filter_by(severity=severity)
    
    # Get total count before limiting
    total = query.count()
    
    # Apply pagination
    complaints = query.offset(offset).limit(limit).all()
    
    return jsonify({
        'total': total,
        'count': len(complaints),
        'offset': offset,
        'limit': limit,
        'complaints': [complaint_to_dict(c) for c in complaints]
    }), 200


@app.route('/api/complaints/<int:complaint_id>/status', methods=['PATCH'])
def update_complaint_status(complaint_id):
    """
    Update the status of a complaint and log the change.
    
    Expected JSON:
    {
        "status": "in_progress",
        "note": "Work started on the pothole"
    }
    
    Returns:
        - 200 with updated complaint data if successful
        - 400 if invalid status
        - 404 if complaint not found
    """
    complaint = Complaint.query.get(complaint_id)
    
    if not complaint:
        return jsonify({'error': f'Complaint {complaint_id} not found'}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    note = data.get('note')
    
    # Validate status
    valid_statuses = ['pending', 'in_progress', 'resolved']
    if new_status not in valid_statuses:
        return jsonify({
            'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
        }), 400
    
    # Update status
    old_status = complaint.status
    complaint.status = new_status
    db.session.commit()
    
    # Log status change to StatusHistory
    status_record = StatusHistory(
        complaint_id=complaint_id,
        status=new_status,
        note=note or f'Status changed from {old_status} to {new_status}'
    )
    db.session.add(status_record)
    db.session.commit()
    
    return jsonify({
        'message': f'Complaint status updated to {new_status}',
        'complaint': complaint_to_dict(complaint)
    }), 200


@app.route('/api/wards/<int:ward_id>/stats', methods=['GET'])
def get_ward_stats(ward_id):
    """
    Get statistics for a specific ward.
    
    Returns statistics including:
        - open_count: number of pending + in_progress complaints
        - resolved_count: number of resolved complaints
        - resolution_rate: percentage of resolved complaints
        - avg_response_days: average days from reported_at to first in_progress status
    
    Returns:
        - 200 with ward statistics if successful
        - 404 if ward not found
    """
    ward = Ward.query.get(ward_id)
    
    if not ward:
        return jsonify({'error': f'Ward {ward_id} not found'}), 404
    
    complaints = Complaint.query.filter_by(ward_id=ward_id).all()
    
    # Count open and resolved
    open_count = len([c for c in complaints if c.status in ['pending', 'in_progress']])
    resolved_count = len([c for c in complaints if c.status == 'resolved'])
    total_count = len(complaints)
    
    # Calculate resolution rate
    resolution_rate = (resolved_count / total_count * 100) if total_count > 0 else 0
    
    # Calculate average response days (from reported_at to first in_progress status)
    response_times = []
    for complaint in complaints:
        # Find the first in_progress status change
        in_progress_history = StatusHistory.query.filter_by(
            complaint_id=complaint.id,
            status='in_progress'
        ).order_by(StatusHistory.timestamp).first()
        
        if in_progress_history and complaint.reported_at:
            response_time_seconds = (in_progress_history.timestamp - complaint.reported_at).total_seconds()
            response_time_days = response_time_seconds / 86400
            response_times.append(response_time_days)
    
    avg_response_days = sum(response_times) / len(response_times) if response_times else 0
    
    return jsonify({
        'ward_id': ward_id,
        'ward_name': ward.name,
        'open_count': open_count,
        'resolved_count': resolved_count,
        'resolution_rate': round(resolution_rate, 2),
        'avg_response_days': round(avg_response_days, 2),
        'total_complaints': total_count
    }), 200


# ============================================================================
# Main Block
# ============================================================================
@app.route("/")
def home():
    return "NagarSeva API is running!"
if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        init_db(app)
        
        # Seed database if empty
        seed_database(app)
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
