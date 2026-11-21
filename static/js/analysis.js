
document.addEventListener("DOMContentLoaded", function () {
    const imageInput = document.getElementById("image");
    const previewContainer = document.getElementById("preview-container");
    const imagePreview = document.getElementById("image-preview");

    if (!imageInput || !previewContainer || !imagePreview) {
        return;
    }

    let currentImageUrl = null;

    imageInput.addEventListener("change", function () {
        const file = this.files[0];

        if (currentImageUrl) {
            URL.revokeObjectURL(currentImageUrl);
            currentImageUrl = null;
        }

        if (!file) {
            imagePreview.removeAttribute("src");
            previewContainer.hidden = true;
            return;
        }

        if (!file.type.startsWith("image/")) {
            alert("Please select a valid image file.");
            this.value = "";
            imagePreview.removeAttribute("src");
            previewContainer.hidden = true;
            return;
        }

        currentImageUrl = URL.createObjectURL(file);
        imagePreview.src = currentImageUrl;
        previewContainer.hidden = false;
    });
});
