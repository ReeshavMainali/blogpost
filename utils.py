import os
import re
import uuid
from PIL import Image
from flask import current_app
import mistune


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def unique_slug(title, model, existing_id=None):
    from models import db
    base = slugify(title)
    slug = base
    counter = 1
    while True:
        q = model.query.filter_by(slug=slug)
        if existing_id:
            q = q.filter(model.id != existing_id)
        if not q.first():
            return slug
        slug = f"{base}-{counter}"
        counter += 1


def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower()
        in current_app.config['ALLOWED_EXTENSIONS']
    )


def save_image(file, folder='profiles', size=(256, 256)):
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    img = Image.open(file)
    img.thumbnail(size, Image.LANCZOS)
    img.save(path)
    return f"{folder}/{filename}"


def render_markdown(text):
    md = mistune.create_markdown(
        plugins=['strikethrough', 'table', 'url'],
    )
    return md(text)
