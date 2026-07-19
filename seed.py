import json
from datetime import datetime, timedelta
from models import db, Ward, Authority, Complaint


def seed_database(app):
    """
    Seed the database with initial data from data/seed_data.json.
    Only runs if tables are empty.
    """
    with app.app_context():
        # Check if tables are empty
        if Ward.query.first() or Authority.query.first() or Complaint.query.first():
            print("Database already contains data. Skipping seed.")
            return
        
        try:
            # Load seed data from JSON
            with open('data/seed_data.json', 'r') as f:
                data = json.load(f)
            
            # Seed Wards
            print("Seeding wards...")
            ward_map = {}  # Map ward_id to database id
            for ward_data in data['wards']:
                ward = Ward(name=ward_data['name'])
                db.session.add(ward)
                db.session.flush()
                ward_map[ward_data['ward_id']] = ward.id
            
            db.session.commit()
            print(f"✓ Inserted {len(data['wards'])} wards")
            
            # Seed Authorities
            print("Seeding authorities...")
            authority_map = {}  # Map authority_id to database id
            for auth_data in data['authorities']:
                # Convert list of categories to comma-separated string
                handles = ','.join(auth_data['handles'])
                authority = Authority(
                    name=auth_data['name'],
                    handles=handles
                )
                db.session.add(authority)
                db.session.flush()
                authority_map[auth_data['authority_id']] = authority.id
            
            db.session.commit()
            print(f"✓ Inserted {len(data['authorities'])} authorities")
            
            # Seed Complaints
            print("Seeding complaints...")
            today = datetime.utcnow().date()
            
            for complaint_data in data['complaints']:
                # Convert reported_days_ago to reported_at datetime
                reported_days_ago = complaint_data['reported_days_ago']
                reported_at = datetime.combine(
                    today - timedelta(days=reported_days_ago),
                    datetime.min.time()
                )
                
                # Map category to authority_id by finding authority that handles this category
                category = complaint_data['category']
                authority_id = None
                for auth_data in data['authorities']:
                    if category in auth_data['handles']:
                        authority_id = authority_map[auth_data['authority_id']]
                        break
                
                if authority_id is None:
                    print(f"⚠ Warning: No authority found for category '{category}'. Skipping complaint {complaint_data['id']}")
                    continue
                
                complaint = Complaint(
                    category=complaint_data['category'],
                    severity=complaint_data['severity'],
                    status=complaint_data['status'],
                    lat=complaint_data['lat'],
                    lng=complaint_data['lng'],
                    description=complaint_data['description'],
                    ward_id=ward_map[complaint_data['ward_id']],
                    authority_id=authority_id,
                    confirm_count=complaint_data.get('confirm_count', 1),
                    anonymous=complaint_data.get('anonymous', False),
                    reported_at=reported_at,
                    photo_path=None,
                    resolved_photo_path=None
                )
                db.session.add(complaint)
            
            db.session.commit()
            print(f"✓ Inserted {len(data['complaints'])} complaints")
            
            print("\n✓ Database seeding completed successfully!")
        
        except FileNotFoundError:
            print("✗ Error: data/seed_data.json not found")
            raise
        except KeyError as e:
            print(f"✗ Error: Missing key in seed data: {e}")
            raise
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during seeding: {e}")
            raise


if __name__ == '__main__':
    from app import app  # Adjust import based on your Flask app location
    seed_database(app)
