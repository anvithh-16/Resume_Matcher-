"""Fill the database named by DATABASE_URL with synthetic jobs for load tests (NFR-01, NFR-02).

Usage:  export DATABASE_URL=sqlite:///./perf.db && python -m scripts.gen_jobs 5000
Owner: Ankitha Revadala.
"""
import random
import sys

from app.db.database import SessionLocal, init_db
from app.db.models import Job

random.seed(42)
TITLES = ["Python Developer", "Data Analyst", "Frontend Engineer", "ML Engineer", "DevOps Engineer",
          "Java Developer", "Backend Intern", "Cloud Engineer", "QA Engineer", "Full Stack Developer"]
SKILLS = ["python", "java", "javascript", "sql", "react", "docker", "aws", "git", "linux", "pandas",
          "machine learning", "fastapi", "node.js", "kubernetes", "excel", "tableau", "spring", "html", "css"]
CITIES = ["Bengaluru", "Hyderabad", "Pune", "Chennai", "Mumbai", "Remote"]
TYPES = ["full-time", "internship", "part-time", "contract"]

init_db()
db = SessionLocal()
n = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
for i in range(n):
    title, skills = random.choice(TITLES), random.sample(SKILLS, 4)
    db.add(Job(title=f"{title} {i}", company=f"Company {i % 300}", location=random.choice(CITIES),
               description=f"{title} role using {', '.join(skills)}.", required_skills=skills,
               employment_type=random.choice(TYPES), source="synthetic", active=True))
db.commit()
print("jobs in database:", db.query(Job).count())
