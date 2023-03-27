// scripts.js
$(document).ready(function () {
    const uploadForm = $("#upload-form");
    const imageInput = $("#image-input");
    const originalImage = $("#original-image");
    const processedImage = $("#processed-image");
    const processImageBtn = $("#process-image");

    uploadForm.on("submit", function (event) {
        event.preventDefault();
        const formData = new FormData();
        formData.append("image", imageInput[0].files[0]);

        axios.post("/upload", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        })
        .then(response => {
            originalImage.attr("src", response.data.url);
            originalImage.show();
            processImageBtn.show();
        })
        .catch(error => {
            console.error(error);
        });
    });

    processImageBtn.on("click", function () {
        const originalImageUrl = originalImage.attr("src");
        axios.post("/process", {url: originalImageUrl})
        .then(response => {
            const processedImageUrl = response.data.url;
            processedImage.attr("src", processedImageUrl);
            processedImage.show();
        })
        .catch(error => {
            console.error(error);
        });
    });
});
