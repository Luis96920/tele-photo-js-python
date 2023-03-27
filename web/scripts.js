// scripts.js
$(document).ready(function () {
    const uploadForm = $("#upload-form");
    const imageInput = $("#image-input");
    const originalImage = $("#original-image");
    const processedImage = $("#processed-image");

    uploadForm.on("submit", function (event) {
        event.preventDefault();
        const formData = new FormData();
        formData.append("image", imageInput[0].files[0]);

        axios.post("/upload_and_process", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        })
        .then(response => {
            originalImage.attr("src", response.data.original_url);
            originalImage.show();
            processedImage.attr("src", response.data.processed_url);
            processedImage.show();
        })
        .catch(error => {
            console.error(error);
        });
    });
});
