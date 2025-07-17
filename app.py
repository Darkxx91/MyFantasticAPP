from flask import Flask, render_template, request, redirect, url_for
from models import db, Project, Scene
import os
import requests

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

def generate_image(prompt):
    # a placeholder image generation service
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    return None

@app.route('/project/<int:project_id>/scene', methods=['POST'])
def new_scene(project_id):
    script_text = request.form['script_text']
    image_data = generate_image(script_text)
    if image_data:
        image_filename = f"scene_{project_id}_{len(Project.query.get(project_id).scenes) + 1}.jpg"
        image_path = os.path.join('static', image_filename)
        with open(image_path, 'wb') as f:
            f.write(image_data)
        scene = Scene(project_id=project_id, script_text=script_text, image_path=image_filename)
    else:
        scene = Scene(project_id=project_id, script_text=script_text)
    db.session.add(scene)
    db.session.commit()
    return redirect(url_for('project_view', project_id=project_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
