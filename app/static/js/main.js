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
