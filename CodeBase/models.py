from extensions import db

class Company(db.Model):
    __tablename__ = 'companies'
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(4096))
    logo_url = db.Column(db.String(4096))
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
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    job_type_id = db.Column(db.Integer, db.ForeignKey('job_types.job_type_id'))
    category_id = db.Column(db.Integer, db.ForeignKey('job_categories.category_id'))
    posted_date = db.Column(db.Date)
    closing_date = db.Column(db.Date)
    salary_min = db.Column(db.Numeric(10, 2))
    salary_max = db.Column(db.Numeric(10, 2))
    is_featured = db.Column(db.Boolean, default=False)
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

class JobType(db.Model):
    __tablename__ = 'job_types'
    job_type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50))

class JobCategory(db.Model):
    __tablename__ = 'job_categories'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100))

class Skill(db.Model):
    __tablename__ = 'skills'
    skill_id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100))

class Tag(db.Model):
    __tablename__ = 'tags'
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(50))

class Benefit(db.Model):
    __tablename__ = 'benefits'
    benefit_id = db.Column(db.Integer, primary_key=True)
    benefit_name = db.Column(db.String(100))

class JobSkill(db.Model):#new
    __tablename__ = 'job_skills'
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.skill_id'), primary_key=True)

company_locations = db.Table('company_locations',
    db.Column('company_id', db.Integer, db.ForeignKey('companies.company_id'), primary_key=True),
    db.Column('location_id', db.Integer, db.ForeignKey('locations.location_id'), primary_key=True)
)

company_industries = db.Table('company_industries',
    db.Column('company_id', db.Integer, db.ForeignKey('companies.company_id'), primary_key=True),
    db.Column('industry_id', db.Integer, db.ForeignKey('industries.industry_id'), primary_key=True)
)