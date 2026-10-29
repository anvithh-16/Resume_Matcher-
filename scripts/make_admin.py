import sys
from app.db.database import SessionLocal, init_db
from app.db.models import User

init_db()
db = SessionLocal()
user = db.query(User).filter_by(email=sys.argv[1].strip().lower()).first()
if user is None:
    sys.exit("No user with that email. Register first.")
user.is_admin = True
db.commit()
print("Now admin:", user.email)
