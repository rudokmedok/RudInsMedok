import os
import secrets
from PIL import Image
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, PostForm, ChangeAvatarForm, ChangePasswordForm, ChangeNicknameForm, \
    SearchForm
from models import db, User, Post, Media

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_post_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_pics', picture_fn)

    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_media_files(form_files, file_type):
    file_paths = []
    for form_file in form_files:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_file.filename)
        file_fn = random_hex + f_ext
        file_path = os.path.join(app.root_path, 'static/media', file_fn)

        if file_type == 'image':
            output_size = (500, 500)
            i = Image.open(form_file)
            i.thumbnail(output_size)
            i.save(file_path)
        else:
            form_file.save(file_path)

        file_paths.append(file_fn)
    return file_paths


@app.route('/')
def index():
    form = SearchForm()
    posts = Post.query.all()
    return render_template('index.html', posts=posts, search_form=form)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.avatar.data:
            picture_file = save_picture(form.avatar.data)
        else:
            picture_file = 'default.jpg'
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(nickname=form.nickname.data, password=hashed_password, avatar=picture_file)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check your nickname and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    posts = []
    if form.validate_on_submit():
        search_term = form.search.data
        posts = Post.query.filter(
            (Post.title.ilike(f'%{search_term}%')) |
            (Post.tags.ilike(f'%{search_term}%'))
        ).all()
    return render_template('search_results.html', form=form, posts=posts, search_form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def show_post(post_id):
    search_form = SearchForm()
    post = Post.query.get_or_404(post_id)
    return render_template('view_post.html', post=post, search_form=search_form)



@app.route('/post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    search_form = SearchForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            tags=form.tags.data,
            author=current_user
        )
        db.session.add(new_post)
        db.session.commit()

        if form.images.data:
            image_files = save_media_files(form.images.data, 'image')
            for image_file in image_files:
                media = Media(file_name=image_file, file_type='image', post_id=new_post.id)
                db.session.add(media)

        if form.videos.data:
            video_files = save_media_files(form.videos.data, 'video')
            for video_file in video_files:
                media = Media(file_name=video_file, file_type='video', post_id=new_post.id)
                db.session.add(media)

        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_post.html', form=form, search_form=search_form)





@app.route('/like/<int:post_id>')
@login_required
def like_post(post_id):
    post = Post.query.get(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/view/<int:post_id>')
@login_required
def view_post(post_id):
    post = Post.query.get(post_id)
    post.views += 1
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You are not authorized to edit this post.', 'danger')
        return redirect(url_for('index'))

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.tags = form.tags.data
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.tags.data = post.tags
    return render_template('edit_post.html', form=form)


@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You are not authorized to delete this post.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = RegistrationForm()
    search_form = SearchForm()
    if form.validate_on_submit():
        if form.avatar.data:
            picture_file = save_picture(form.avatar.data)
            current_user.avatar = picture_file
        current_user.nickname = form.nickname.data
        if form.password.data:
            current_user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.nickname.data = current_user.nickname
    return render_template('edit_profile.html', form=form, search_form=search_form)




@app.route('/change_nickname', methods=['GET', 'POST'])
@login_required
def change_nickname():
    search_form = SearchForm()
    form = ChangeNicknameForm()
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        db.session.commit()
        flash('Nickname updated successfully!', 'success')
        return redirect(url_for('edit_profile'))
    return render_template('change_nickname.html', form=form, search_form=search_form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    search_form = SearchForm()
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Password updated successfully!', 'success')
        return redirect(url_for('edit_profile'))
    return render_template('change_password.html', form=form, search_form=search_form)

@app.route('/change_avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    search_form = SearchForm()
    form = ChangeAvatarForm()
    if form.validate_on_submit():
        if form.avatar.data:
            picture_file = save_picture(form.avatar.data)
            current_user.avatar = picture_file
        db.session.commit()
        flash('Avatar updated successfully!', 'success')
        return redirect(url_for('edit_profile'))
    return render_template('change_avatar.html', form=form, search_form=search_form)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)