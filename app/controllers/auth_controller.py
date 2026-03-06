from flask import render_template


class AuthController:
    def login_page(self):
        return render_template("login.html")

    def register_page(self):
        return render_template("register.html")


_auth_controller = AuthController()


def login_page():
    return _auth_controller.login_page()


def register_page():
    return _auth_controller.register_page()
