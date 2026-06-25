from app import create_app
from app.services.pemeriksaan_job_service import PemeriksaanJobService


def main():
    app = create_app()

    with app.app_context():
        deleted_count = PemeriksaanJobService().cleanup_expired_jobs()
        print(f"Cleanup menghapus {deleted_count} job kedaluwarsa.")


if __name__ == "__main__":
    main()
