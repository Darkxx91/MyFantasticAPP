from flask import Flask, render_template, request, redirect, url_for
from models import db, Project, Scene
import os
import requests
from generate.platforms import minimax

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
    client = minimax(api_key="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJBbmRyZWkgTWxhZGluIiwiVXNlck5hbWUiOiJBbmRyZWkgTWxhZGluIiwiQWNjb3VudCI6IiIsIlN1YmplY3RJRCI6IjE4NjMxNDA5MzIxNjE5MDA5MDkiLCJQaG9uZSI6IiIsIkdyb3VwSUQiOiIxODYzMTQwOTMyMTUzNTEyMzAxIiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiZGFya3h4MTk5MUBnbWFpbC5jb20iLCJDcmVhdGVUaW1lIjoiMjAyNS0wNy0xNyAxMzowODoxMiIsIlRva2VuVHlwZSI6MSwiaXNzIjoibWluaW1heCJ9.q5dao_RgzQWkiL5c5ps6h77cP10ABn0F7yWLIC3ANryzWxkNcGrz2t1OlDr_HlbzDv_BfE7VJlrZUPBWH4lsFLuI8KvCUwQXGh_c2Ua8z8vts6Y7d_kpfisX4RVa90iqQQL9RnsgMQXPhPSNyq6n4rq_paXB-XuBPJwCng1xH_8abVJyVWxdA4yqXxP2JxWHrhAuqE1ZE4RFABhemGIOJUFiwWoXGUhhXk9c7aLjiGHrY-1cj3c2t0Rm9e13E--ebJVMMwLzwDvMrVTaGIDm-w4b0ci_J1vi6rnXFj__ct-GfWxR1rwHPXSsiq-5Vizib32_WYb9CaIZCyY59Cxayw")
    response = client.images.generate(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    image_data = requests.get(image_url).content
    return image_data

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
