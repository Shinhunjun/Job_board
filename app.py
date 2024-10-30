from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():  # put application's code here
    return render_template('index2.html')

@app.route('/jobsearch')
def jobsearch():  # put application's code here
    return render_template('jobsearch.html')

if __name__ == '__main__':
    app.run(debug=True)
