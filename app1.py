from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates')

# Local MySQL connection settings
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@localhost:{port}/{databasename}".format(
    username="root",
    password="Tlsguswns97!",
    port="3306",
    databasename="jobboard",
)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Model class definitions
class Company(db.Model):
    __tablename__ = 'companies'
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))

class Job(db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(4096), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False)
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(50))
    experience_level = db.Column(db.String(50))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    posted_date = db.Column(db.Date)
    education_level = db.Column(db.String(100))
    remote = db.Column(db.String(50))
    company = db.relationship('Company', backref='jobs')

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))

# CSV data loading and insertion function
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, 'db_test.csv')

def load_data_from_csv():
    data = pd.read_csv(csv_path)
    for _, row in data.iterrows():
        # Insert or update company information
        existing_company = Company.query.get(row['company_id'])
        if not existing_company:
            company = Company(
                company_id=row['company_id'],
                name=row['company_name'],
                industry=row['industry'],
                size=row['company_size']
            )
            db.session.add(company)
        else:
            existing_company.name = row['company_name']
            existing_company.industry = row['industry']
            existing_company.size = row['company_size']
        
        # Insert job information
        job = Job(
            job_id=row['job_id'],
            title=row['title'],
            description=row['description'],
            company_id=row['company_id'],
            location=row['location'],
            job_type=row['job_type'],
            experience_level=row['experience_level'],
            salary_min=row['salary_min'] if not pd.isna(row['salary_min']) else None,
            salary_max=row['salary_max'] if not pd.isna(row['salary_max']) else None,
            posted_date=datetime.strptime(row['posted_date'], '%Y-%m-%d').date() if not pd.isna(row['posted_date']) else None,
            education_level=row['education_level'],
            remote=row['remote']
        )
        db.session.add(job)

    db.session.commit()

# Create tables and load CSV data
with app.app_context():
    db.drop_all()
    db.create_all()
    load_data_from_csv()

# Basic route
@app.route('/')
def index():
    return render_template('index2.html')

# Job search route
@app.route('/jobsearch', methods=['GET'])
def jobsearch():
    keywords = request.args.get('keywords', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    industry = request.args.get('industry', '')
    experience_level = request.args.get('experience_level', '')
    
    # Set base query
    jobs_query = Job.query.join(Company).add_columns(
        Job.job_id, Job.title, Job.description, Job.company_id, Company.name.label('company_name')
    )

    # Apply filter conditions
    if keywords:
        jobs_query = jobs_query.filter(Job.title.ilike(f'%{keywords}%'))
    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f'%{location}%'))
    if job_type:
        jobs_query = jobs_query.filter(Job.job_type == job_type)
    if industry:
        jobs_query = jobs_query.filter(Company.industry == industry)
    if experience_level:
        jobs_query = jobs_query.filter(Job.experience_level == experience_level)

    jobs = jobs_query.all()
    
    # Pass filter selections to the template to keep them displayed
    return render_template('jobsearch.html', jobs=jobs, keywords=keywords, location=location, job_type=job_type, industry=industry, experience_level=experience_level)

# Comments page route
@app.route("/comments_page", methods=["GET", "POST"])
def comments_page():
    if request.method == "GET":
        return render_template("comments_page.html", comments=Comment.query.all())

    comment_content = request.form.get("contents")
    if comment_content:
        comment = Comment(content=comment_content)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('comments_page'))

if __name__ == '__main__':
    app.run(debug=True)