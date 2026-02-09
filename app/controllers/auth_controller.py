from flask import render_template


def login_page():
    return render_template("login.html")


def register_page():
    return render_template("register.html")
