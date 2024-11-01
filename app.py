from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="ddanielhasan",
    password="danieljun123!",
    hostname="ddanielhasan.mysql.pythonanywhere-services.com",
    databasename="ddanielhasan$comments",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/jobsearch')
def jobsearch():
    return render_template('jobsearch.html')

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

