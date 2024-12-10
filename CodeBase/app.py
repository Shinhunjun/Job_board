from flask import Flask, render_template, redirect, request, url_for, flash
from extensions import db
from models import Company, Job, Location, JobType, JobCategory
from utils import load_company_data_to_db, load_job_data_to_db
import os
from werkzeug.utils import secure_filename


app = Flask(__name__, template_folder='templates')
app.secret_key = "super secret key"

#Daniel local connection:
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@localhost:{port}/{databasename}".format(
    username="root",
    password="12345678",
    port="3306",
    databasename="jobboard2",
)


app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

############ ROUTES ##############

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/jobsearch', methods=['GET'])
def jobsearch():
    keywords = request.args.get('keywords', '')
    job_category = request.args.get('job_category', '')
    # Query with outer joins
    jobs_query = (
        Job.query
        .join(Company)
        .outerjoin(Location, Job.location_id == Location.location_id)
        .outerjoin(JobType, Job.job_type_id == JobType.job_type_id)
        .outerjoin(JobCategory, Job.category_id == JobCategory.category_id)
        .add_columns(
            Job.job_id,
            Job.title,
            Job.description,
            Job.company_id,
            Job.salary_min,
            Job.salary_max,
            Company.name.label('company_name'),
            Company.logo_url.label('company_logo'),
            Location.city.label('location_city'),
            Location.state.label('location_state'),
            Location.country.label('location_country'),
            JobType.type_name.label('job_type'),
            JobCategory.category_name.label('job_category')
        )
    )
    if keywords:
        jobs_query = jobs_query.filter(Job.title.ilike(f'%{keywords}%'))
    if job_category:
        jobs_query = jobs_query.filter(JobCategory.category_name.ilike(job_category))

    categories = JobCategory.query.all()
    jobs = jobs_query.all()
    return render_template('jobsearch.html', jobs=jobs, categories=categories, job_category=job_category)

@app.route('/job/<int:job_id>', methods=['GET'])
def job_details(job_id):
    # Fetch the job details by ID
    job = (
        Job.query
        .join(Company)
        .outerjoin(Location, Job.location_id == Location.location_id)
        .outerjoin(JobType, Job.job_type_id == JobType.job_type_id)
        .outerjoin(JobCategory, Job.category_id == JobCategory.category_id)
        .add_columns(
            Job.job_id,
            Job.title,
            Job.description,
            Job.company_id,
            Company.name.label('company_name'),
            Company.logo_url.label('company_logo'),
            Location.city.label('location_city'),
            Location.state.label('location_state'),
            Location.country.label('location_country'),
            JobType.type_name.label('job_type'),
            JobCategory.category_name.label('job_category'),
            Job.salary_min,
            Job.salary_max,
            Job.posted_date,
            Job.closing_date
        )
        .filter(Job.job_id == job_id)
        .first_or_404()
    )

    return render_template('job_details.html', job=job)

@app.route('/companies')
def companies_page():
    companies = Company.query.all()
    return render_template('companies.html', companies=companies)

@app.route('/company/<int:company_id>')
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    # No need for extra queries since we have relationships defined
    return render_template('company_detail.html',
                         company=company,
                         jobs=company.jobs,
                         locations=company.locations,
                         industries=company.industries)



ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        upload_type = request.form.get('upload_type')
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            file.save(file_path)

            try:
                if upload_type == 'company':
                    load_company_data_to_db(file_path)
                    flash('Company data successfully uploaded and processed')
                elif upload_type == 'job':
                    load_job_data_to_db(file_path)
                    flash('Job data successfully uploaded and processed')
                else:
                    flash('Invalid upload type')
                    return redirect(request.url)
            except Exception as e:
                flash(f'Error processing file: {e}')

            return redirect(url_for('upload_file'))

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)

