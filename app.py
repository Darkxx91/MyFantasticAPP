from flask import Flask, render_template, request, redirect, url_for
from models import db, Project, Scene
import os
import requests
from generate.platforms import minimax
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

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

@app.route('/scene/<int:scene_id>/animate', methods=['POST'])
def animate_scene(scene_id):
    scene = Scene.query.get_or_404(scene_id)
    # This is a placeholder for the actual RunwayML API call
    # We would need to replace this with the actual API endpoint and authentication
    video_url = "https://www.w3schools.com/html/mov_bbb.mp4"
    video_data = requests.get(video_url).content
    if video_data:
        video_filename = f"scene_{scene.project_id}_{scene.id}.mp4"
        video_path = os.path.join('static', video_filename)
        with open(video_path, 'wb') as f:
            f.write(video_data)
        scene.video_path = video_filename
        db.session.commit()
    return redirect(url_for('project_view', project_id=scene.project_id))

@app.route('/project/<int:project_id>/create_movie', methods=['POST'])
def create_movie(project_id):
    project = Project.query.get_or_404(project_id)
    clips = []
    for scene in project.scenes:
        if scene.video_path:
            clips.append(VideoFileClip(os.path.join('static', scene.video_path)))

    if clips:
        final_clip = CompositeVideoClip(clips)
        movie_filename = f"project_{project_id}_movie.mp4"
        movie_path = os.path.join('static', movie_filename)
        final_clip.write_videofile(movie_path)
        return redirect(url_for('movie_view', movie_filename=movie_filename))

    return redirect(url_for('project_view', project_id=project_id))

@app.route('/movie/<movie_filename>')
def movie_view(movie_filename):
    return render_template('movie_view.html', movie_filename=movie_filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
