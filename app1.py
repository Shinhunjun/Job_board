from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np

app = Flask(__name__, template_folder='templates')

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

# Database models
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))

class Company(db.Model):
    __tablename__ = 'companies'
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)  
    description = db.Column(db.Text)
    website = db.Column(db.String(1024))  # 길이 제한을 늘림
    logo_url = db.Column(db.String(255))
    jobs = db.relationship('Job', back_populates='company', lazy=True)
    locations = db.relationship('Location',
                                secondary='company_locations',
                                backref=db.backref('companies', lazy=True))
    industries = db.relationship('Industry',
                                 secondary='company_industries',
                                 backref=db.backref('companies', lazy=True))



class Job(db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(4096), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False)
    company = db.relationship('Company', back_populates='jobs')

class Location(db.Model):
    __tablename__ = 'locations'
    location_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), nullable=False)

class Industry(db.Model):
    __tablename__ = 'industries'
    industry_id = db.Column(db.Integer, primary_key=True)
    industry_name = db.Column(db.String(100), nullable=False)

company_locations = db.Table('company_locations',
    db.Column('company_id', db.Integer, db.ForeignKey('companies.company_id'), primary_key=True),
    db.Column('location_id', db.Integer, db.ForeignKey('locations.location_id'), primary_key=True)
)

company_industries = db.Table('company_industries',
    db.Column('company_id', db.Integer, db.ForeignKey('companies.company_id'), primary_key=True),
    db.Column('industry_id', db.Integer, db.ForeignKey('industries.industry_id'), primary_key=True)
)

def load_excel_data_to_db(excel_path):
    df = pd.read_excel(excel_path)

    for _, row in df.iterrows():
        # 웹사이트 URL 길이 확인 및 자르기
        website = row['company_website-href']
        if pd.notna(website) and len(website) > 1024:
            website = website[:1024]  # 1024자를 초과할 경우 잘라냄

        # 회사 정보 생성
        company = Company(
            name=row['company_title'],
            description=row['company_overview_cleaned'] if pd.notna(row['company_overview_cleaned']) else None,
            website=website,
            logo_url=row['company_logo-src']
        )
        db.session.add(company)
        db.session.flush()  # company_id 생성 후 사용 가능

        # 위치 정보 처리 및 추가
        if pd.notna(row['company_location']):
            location_parts = row['company_location'].split(',')
            location = Location(
                city=location_parts[0].strip() if len(location_parts) > 0 else None,
                state=location_parts[1].strip() if len(location_parts) > 1 else None,
                country=location_parts[2].strip() if len(location_parts) > 2 else ""  # country가 없으면 빈 문자열로 설정
            )
            db.session.add(location)
            db.session.flush()  # location_id 생성 후 사용 가능

            # company와 location 연결
            db.session.execute(company_locations.insert().values(
                company_id=company.company_id, location_id=location.location_id
            ))

        # 산업 정보 처리 및 추가
        if pd.notna(row['primary_company_category']):
            industry = Industry(industry_name=row['primary_company_category'])
            db.session.add(industry)
            db.session.flush()  # industry_id 생성 후 사용 가능

            # company와 industry 연결
            db.session.execute(company_industries.insert().values(
                company_id=company.company_id, industry_id=industry.industry_id
            ))

    # 변경 사항 커밋
    db.session.commit()
    
# Routes and application logic
@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/jobsearch', methods=['GET'])
def jobsearch():
    keywords = request.args.get('keywords', '')
    jobs_query = Job.query.join(Company).add_columns(Job.job_id, Job.title, Job.description, Job.company_id, Company.name.label('company_name'))
    if keywords:
        jobs_query = jobs_query.filter(Job.title.ilike(f'%{keywords}%'))
    jobs = jobs_query.all()
    return render_template('jobsearch.html', jobs=jobs)

@app.route('/companies')
def companies():
    companies = Company.query.all()
    return render_template('companies.html', companies=companies)

@app.route('/company/<int:company_id>')
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('company_detail.html', company=company, jobs=company.jobs, locations=company.locations, industries=company.industries)

@app.route("/comments_page", methods=["GET", "POST"])
def comments_page():
    if request.method == "GET":
        return render_template("comments_page.html", comments=Comment.query.all())
    comment = Comment(content=request.form["contents"])
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('comments_page'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_excel_data_to_db('/Users/hunjunsin/Desktop/box/Introduction_DMB/project/ddanielhasan.github.io/data/cleaned_company_data.xlsx')  # Replace with actual path
    app.run(debug=True)