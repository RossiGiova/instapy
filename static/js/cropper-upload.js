/*
 * Square-crops the chosen image with Cropper.js and, on submit, swaps the
 * cropped file into the form's <input type="file"> so Django receives a
 * normal multipart upload. Used by the "new post" and "edit profile" forms.
 */
(function () {
    "use strict";

    const form = document.querySelector(".js-cropper-form");
    if (!form || typeof Cropper === "undefined") return;

    const fileInput = form.querySelector('input[type="file"]');
    const image = form.querySelector(".js-cropper-image");
    const SIZE = 640;
    let cropper = null;

    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        if (!file || !file.type.startsWith("image/")) return;

        const reader = new FileReader();
        reader.addEventListener("load", () => {
            image.hidden = false;
            image.src = reader.result;
            cropper = new Cropper(image, { aspectRatio: 1, viewMode: 2 });
        });
        reader.readAsDataURL(file);
    });

    form.addEventListener("submit", (event) => {
        if (!cropper) return; // nothing to crop: submit as usual
        event.preventDefault();
        cropper.getCroppedCanvas({ width: SIZE, height: SIZE }).toBlob((blob) => {
            const transfer = new DataTransfer();
            transfer.items.add(new File([blob], "image.jpg", { type: "image/jpeg" }));
            fileInput.files = transfer.files;
            cropper.destroy();
            cropper = null;
            form.submit();
        }, "image/jpeg", 0.92);
    });
})();
