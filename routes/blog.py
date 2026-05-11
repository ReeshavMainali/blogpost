from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy import desc, or_
from models import db, Post, User, Like, Comment, View
from utils import unique_slug, allowed_file, save_image, render_markdown
import json

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get all posts and sort by trending score
    all_posts = Post.query.all()
    trending = sorted(all_posts, key=lambda p: p.trending_score, reverse=True)
    
    # Paginate trending
    total_trending = len(trending)
    start = (page - 1) * per_page
    end = start + per_page
    trending_page = trending[start:end]
    total_pages = (total_trending + per_page - 1) // per_page
    
    # Recent posts (no pagination)
    recent = Post.query.order_by(desc(Post.created_at)).limit(10).all()
    
    return render_template('blog/index.html', 
                         trending=trending_page, 
                         recent=recent,
                         current_page=page,
                         total_pages=total_pages,
                         total_trending=total_trending)


@blog_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    posts = []
    writers = []
    post_page = page
    post_total_pages = 0
    post_total = 0
    
    if q:
        # Search posts by title or content
        all_posts = Post.query.filter(
            or_(
                Post.title.ilike(f'%{q}%'),
                Post.content.ilike(f'%{q}%')
            )
        ).order_by(desc(Post.views)).all()
        
        post_total = len(all_posts)
        start = (page - 1) * per_page
        end = start + per_page
        posts = all_posts[start:end]
        post_total_pages = (post_total + per_page - 1) // per_page
        
        # Search writers by username or bio
        writers = User.query.filter(
            or_(
                User.username.ilike(f'%{q}%'),
                User.bio.ilike(f'%{q}%')
            )
        ).all()
    
    return render_template('blog/search.html', 
                         query=q, 
                         posts=posts, 
                         writers=writers,
                         current_page=page,
                         total_pages=post_total_pages,
                         total_posts=post_total)


@blog_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            flash('Title and content are required.', 'error')
            return render_template('blog/editor.html', post=None)

        post = Post(
            title=title,
            content=content,
            slug=unique_slug(title, Post),
            user_id=current_user.id,
        )

        file = request.files.get('cover_image')
        if file and file.filename and allowed_file(file.filename):
            post.cover_image = save_image(file, folder='posts')

        db.session.add(post)
        db.session.commit()
        flash('Post published!', 'success')
        return redirect(url_for('blog.post_detail', slug=post.slug))

    return render_template('blog/editor.html', post=None)


@blog_bp.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    
    should_increment = False
    
    # Track views for authenticated users
    if current_user.is_authenticated:
        existing_view = View.query.filter_by(user_id=current_user.id, post_id=post.id).first()
        if not existing_view:
            should_increment = True
            db.session.add(View(user_id=current_user.id, post_id=post.id))
    else:
        # Track views for unauthenticated users using cookies
        viewed_posts = request.cookies.get('viewed_posts', '{}')
        try:
            viewed_posts = json.loads(viewed_posts)
        except:
            viewed_posts = {}
        
        post_id_str = str(post.id)
        if post_id_str not in viewed_posts:
            should_increment = True
            viewed_posts[post_id_str] = True
    
    if should_increment:
        post.views += 1
    
    db.session.commit()

    content_html = render_markdown(post.content)
    top_comments = (
        Comment.query
        .filter_by(post_id=post.id, parent_id=None)
        .order_by(Comment.created_at)
        .all()
    )
    liked = False
    if current_user.is_authenticated:
        liked = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first() is not None

    response = make_response(render_template(
        'blog/post.html',
        post=post,
        content_html=content_html,
        comments=top_comments,
        liked=liked,
    ))
    
    # Set cookie for unauthenticated users
    if not current_user.is_authenticated:
        response.set_cookie('viewed_posts', json.dumps(viewed_posts), max_age=30*24*60*60)
    
    return response


@blog_bp.route('/post/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            flash('Title and content are required.', 'error')
            return render_template('blog/editor.html', post=post)

        post.title = title
        post.content = content
        if title != post.title:
            post.slug = unique_slug(title, Post, existing_id=post.id)

        file = request.files.get('cover_image')
        if file and file.filename and allowed_file(file.filename):
            post.cover_image = save_image(file, folder='posts')

        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('blog.post_detail', slug=post.slug))

    return render_template('blog/editor.html', post=post)


@blog_bp.route('/post/<slug>/delete', methods=['POST'])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.user_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('blog.index'))


@blog_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        db.session.delete(like)
        liked = False
    else:
        db.session.add(Like(user_id=current_user.id, post_id=post_id))
        liked = True
    db.session.commit()
    return jsonify({'liked': liked, 'count': post.like_count})


@blog_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    body = request.form.get('body', '').strip()
    parent_id = request.form.get('parent_id', type=int)

    if not body:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('blog.post_detail', slug=post.slug))

    if parent_id:
        parent = Comment.query.get_or_404(parent_id)
        if parent.post_id != post_id:
            abort(400)

    comment = Comment(
        body=body,
        user_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id if parent_id else None,
    )
    db.session.add(comment)
    db.session.commit()
    flash('Comment added.', 'success')
    return redirect(url_for('blog.post_detail', slug=post.slug) + '#comments')


@blog_bp.route('/post/<int:post_id>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(post_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        abort(403)
    post = Post.query.get_or_404(post_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect(url_for('blog.post_detail', slug=post.slug) + '#comments')
