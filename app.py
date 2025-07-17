from flask import Flask, render_template, request, redirect, url_for
from models import db, Project

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
db.init_app(app)

@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

@app.route('/project', methods=['POST'])
def new_project():
    title = request.form['title']
    description = request.form['description']
    project = Project(title=title, description=description)
    db.session.add(project)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/project/<int:project_id>')
def project_view(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_view.html', project=project)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
