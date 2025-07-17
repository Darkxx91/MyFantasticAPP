from flask import Flask, render_template
from models import db, Project

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
db.init_app(app)

@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

if __name__ == '__main__':
    app.run(debug=True)
