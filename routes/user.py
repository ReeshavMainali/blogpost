from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Post
from utils import allowed_file, save_image

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template('user/profile.html', profile_user=user, posts=posts)


@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()
        current_user.bio = bio

        file = request.files.get('profile_picture')
        if file and file.filename and allowed_file(file.filename):
            current_user.profile_picture = save_image(file, folder='profiles')

        new_password = request.form.get('new_password', '')
        if new_password:
            confirm = request.form.get('confirm_password', '')
            current_password = request.form.get('current_password', '')
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('user/settings.html')
            if new_password != confirm:
                flash('New passwords do not match.', 'error')
                return render_template('user/settings.html')
            current_user.set_password(new_password)

        db.session.commit()
        flash('Settings saved.', 'success')
        return redirect(url_for('user.settings'))

    return render_template('user/settings.html')
