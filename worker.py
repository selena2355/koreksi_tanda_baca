import time
import traceback


def main():
    print("Memulai worker pemeriksaan dokumen...", flush=True)

    from app import create_app
    from app.services.pemeriksaan_job_service import PemeriksaanJobService

    print("Membuat Flask app untuk worker...", flush=True)
    app = create_app()

    with app.app_context():
        print("Menginisialisasi service worker...", flush=True)
        service = PemeriksaanJobService()
        print("Worker pemeriksaan dokumen berjalan. Tekan Ctrl+C untuk berhenti.", flush=True)
        last_idle_log = 0
        last_cleanup = 0

        while True:
            try:
                now = time.time()
                if now - last_cleanup >= 300:
                    deleted_count = service.cleanup_expired_jobs()
                    if deleted_count:
                        print(f"Cleanup menghapus {deleted_count} job kedaluwarsa.", flush=True)
                    last_cleanup = now

                job = service.ambil_job_berikutnya()
                if not job:
                    if now - last_idle_log >= 10:
                        print("Tidak ada job pending. Worker menunggu...", flush=True)
                        last_idle_log = now
                    time.sleep(2)
                    continue

                print(f"Mengambil job #{job.id}: {job.nama_dokumen}", flush=True)
                service.proses_job(job)
                print(f"Job #{job.id} selesai dengan status: {job.status}", flush=True)
            except KeyboardInterrupt:
                print("Worker dihentikan.", flush=True)
                break
            except Exception:
                traceback.print_exc()
                time.sleep(2)


if __name__ == "__main__":
    main()
