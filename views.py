from flask import flash, redirect, render_template, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from __init__ import app, db
from forms import LoginForm, ModifyForm, NoteForm, SignUpForm
from models import Note, User

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.route("/")
def main_page():
    return render_template("index.html", auth_status=current_user.is_authenticated)


@app.route("/signup/", methods=("GET", "POST"))
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for("main_page"))
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        username_exists = db.session.query(
            db.exists().where(User.username == username)
        ).scalar()
        email_exists = db.session.query(db.exists().where(User.email == email)).scalar()
        if username_exists:
            flash("Username already exists", "warning")
        if email_exists:
            flash("Email already exists", "warning")
        if any((username_exists, email_exists)):
            return render_template("signup.html", form=form)

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("SIGNUP SUCCESSFUL", "success")
        return redirect(url_for("main_page", auth_status=current_user.is_authenticated))
    return render_template("signup.html", form=form)


@app.route("/login/", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main_page"))
    form = LoginForm()
    if form.validate_on_submit():

        user = (
            db.session.query(User).filter(User.username == form.username.data).first()
        )
        if not user:
            flash("User not found", "warning")
            return render_template("login.html", form=form)
        if not user.check_password(form.password.data):
            flash("Wrong password", "warning")
            return render_template("login.html", form=form)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("LOGIN SUCCESSFUL", "success")
            return redirect(url_for("main_page"))

    return render_template("login.html", form=form)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main_page"))


@app.route("/notes/new/", methods=("GET", "POST"))
@login_required
def new_note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            color=form.color.data,
            user_id=current_user.id,
        )
        db.session.add(note)
        db.session.commit()
        flash("NOTE ADDED", "success")
        return redirect(url_for("notes"))
    return render_template(
        "newnote.html", form=form, auth_status=current_user.is_authenticated
    )


@app.route("/archive/")
@login_required
def archive():
    data = (
        db.session.query(Note)
        .filter(Note.user_id == current_user.id, Note.archived == True)
        .order_by(Note.updated_on.desc())
    )
    return render_template(
        "archive.html", data=data, auth_status=current_user.is_authenticated
    )


@app.route("/notes/")
@login_required
def notes():
    data = (
        db.session.query(Note)
        .filter(Note.user_id == current_user.id, Note.archived == False)
        .order_by(Note.updated_on.desc())
    )
    return render_template(
        "notes.html", data=data, auth_status=current_user.is_authenticated
    )


@app.route("/notes/<int:note_id>/", methods=("GET", "POST"))
@login_required
def note(note_id):
    modify_form = ModifyForm()
    note = (
        db.session.query(Note)
        .filter(Note.user_id == current_user.id, Note.id == note_id)
        .first_or_404()
    )
    if modify_form.delete.data:
        db.session.delete(note)
        db.session.commit()
        flash("NOTE DELETED", "success")
        return redirect(url_for("notes", auth_status=current_user.is_authenticated))

    if modify_form.archive.data:
        note.archived = not note.archived
        db.session.add(note)
        db.session.commit()
        flash("NOTE ARCHIVED", "success")
        return redirect(url_for("notes", auth_status=current_user.is_authenticated))

    return render_template(
        "note.html",
        note=note,
        form=modify_form,
        auth_status=current_user.is_authenticated,
    )


@app.route("/notes/edit/<int:note_id>/", methods=("GET", "POST"))
@login_required
def edit_note(note_id):
    editor = NoteForm()
    note = (
        db.session.query(Note)
        .filter(Note.user_id == current_user.id, Note.id == note_id)
        .first_or_404()
    )
    if editor.content.data and editor.is_submitted():
        note.title = editor.title.data
        note.content = editor.content.data
        note.color = editor.color.data
        db.session.add(note)
        db.session.commit()
        flash("NOTE EDITED", "success")
        return redirect(url_for("notes", auth_status=current_user.is_authenticated))

    editor.title.data = note.title
    editor.content.data = note.content
    editor.color.data = note.color

    return render_template(
        "edit_note.html",
        note=note,
        form=editor,
        auth_status=current_user.is_authenticated,
    )


@app.errorhandler(404)
def http_404_handler(error):
    return "<h1>HTTP 404 Error GODDAMN</h1>", 404


@app.errorhandler(401)
def http_401_handler(error):
    flash("Login required", "warning")
    return redirect(url_for("login"))
