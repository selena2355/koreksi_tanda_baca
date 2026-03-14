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

const checkForm = document.querySelector(".check-form");
const slowMessage = document.getElementById("slow-message");
if (checkForm && slowMessage) {
    let slowTimer = null;

    const hideMessage = () => {
        slowMessage.classList.remove("is-visible");
    };

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
