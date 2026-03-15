from flask import render_template, redirect, url_for, session, flash


class RiwayatController:
    def riwayat_page(self):
        if not session.get("user_id"):
            flash("Silakan login terlebih dahulu untuk melihat riwayat.", "error")
            return redirect(url_for("auth.login_page"))
        return render_template("riwayat.html")


_riwayat_controller = RiwayatController()


def riwayat_page():
    return _riwayat_controller.riwayat_page()
