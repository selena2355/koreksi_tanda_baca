from flask import render_template


class RiwayatController:
    def riwayat_page(self):
        return render_template("riwayat.html")


_riwayat_controller = RiwayatController()


def riwayat_page():
    return _riwayat_controller.riwayat_page()
