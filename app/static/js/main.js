// Digunakan untuk mengirimkan form secara otomatis saat file dipilih
const docInput = document.getElementById("doc-input");
if (docInput) {
    docInput.addEventListener("change", () => {
        if (docInput.files && docInput.files.length > 0) {
            const uploadForm = document.getElementById("upload-form");
            if (uploadForm) {
                uploadForm.submit();
            }
        }
    });
}

// Menampilkan pesan jika proses upload memakan waktu lebih dari 10 detik
const checkForm = document.querySelector(".check-form");
const slowMessage = document.getElementById("slow-message");
if (checkForm && slowMessage) {
    let slowTimer = null;

    // Fungsi untuk menyembunyikan pesan
    const hideMessage = () => {
        slowMessage.classList.remove("is-visible");
    };

    // Fungsi untuk menjadwalkan tampilan pesan setelah 10 detik
    const scheduleMessage = () => {
        hideMessage();
        if (slowTimer) {
            window.clearTimeout(slowTimer);
        }
        slowTimer = window.setTimeout(() => {
            slowMessage.classList.add("is-visible");
        }, 10000);
    };

    checkForm.addEventListener("submit", () => {
        scheduleMessage();
    });

    window.addEventListener("pageshow", () => {
        hideMessage();
        if (slowTimer) {
            window.clearTimeout(slowTimer);
            slowTimer = null;
        }
    });
}
