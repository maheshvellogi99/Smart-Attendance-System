import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase with your credentials
cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'xyz'  # Replace with your Firebase database URL
})

def get_database():
    """Returns the Firebase database reference."""
    return db.reference() 