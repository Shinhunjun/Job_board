from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')

#daniel local connection:
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@localhost:{port}/{databasename}".format(
    username="root",
    password="12345678",
    port="3306",
    databasename="jobboard2",
)
'''
#Jun local connection:
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@localhost:{port}/{databasename}".format(
    username="root",
    password="12345678",
    port="3306",
    databasename="jobboard2",
)
#prodaction connection:
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="ddanielhasan",
    password="danieljun123!",
    hostname="ddanielhasan.mysql.pythonanywhere-services.com",
    databasename="ddanielhasan$comments",
)'''
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))

class Company(db.Model):
    __tablename__ = 'companies'
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class Job(db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False)
    company = db.relationship('Company', backref='jobs')
@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/jobsearch', methods=['GET'])
def jobsearch():
    keywords = request.args.get('keywords', '')
    # Query with filter if keywords are provided
    jobs_query = Job.query.join(Company).add_columns(Job.job_id, Job.title, Job.description,Job.company_id, Company.name.label('company_name'))
    if keywords:
        jobs_query = jobs_query.filter(Job.title.ilike(f'%{keywords}%'))

    # Add other filters here as needed, similar to the keywords filter
    jobs = jobs_query.all()
    return render_template('jobsearch.html', jobs=jobs)

@app.route("/comments_page", methods=["GET", "POST"])
def comments_page():
    if request.method == "GET":
        return render_template("comments_page.html", comments=Comment.query.all())

    comment = Comment(content=request.form["contents"])
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('comments_page'))

if __name__ == '__main__':
    app.run(debug=True)

