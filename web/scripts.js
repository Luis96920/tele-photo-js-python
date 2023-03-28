// scripts.js
$(document).ready(function () {
    const uploadForm = $("#upload-form");
    const imageInput = $("#image-input");
    const originalImage = $("#original-image");
    const processedImage = $("#processed-image");

    const termsCheckbox = $('#terms');
    const uploadBtn = $('#uploadBtn');

    // Initially disable the button
    uploadBtn.prop('disabled', true);
    uploadBtn.addClass('disabled-btn');

    termsCheckbox.on('change', function () {
      // Enable or disable the button based on the checkbox state
      uploadBtn.prop('disabled', !termsCheckbox.prop('checked'));
  
      // Add or remove the disabled-btn class based on the checkbox state
      if (termsCheckbox.prop('checked')) {
        uploadBtn.removeClass('disabled-btn');
      } else {
        uploadBtn.addClass('disabled-btn');
      }
    });

    // Find the loading-icon element
    const loadingIcon = document.getElementById("loading-icon");

    // Function to show the loading icon
    function showLoadingIcon() {
    loadingIcon.style.display = "block";
    }

    // Function to hide the loading icon
    function hideLoadingIcon() {
    loadingIcon.style.display = "none";
    }

    uploadForm.on("submit", function (event) {
        showLoadingIcon();
        event.preventDefault();
        const formData = new FormData();
        formData.append("image", imageInput[0].files[0]);

        axios.post("https://telephoto.reiform.com/api/upload_and_process", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        })
        .then(response => {
            originalImage.attr("src", response.data.original_url);
            originalImage.show();
            processedImage.attr("src", response.data.processed_url);
            processedImage.show();
            hideLoadingIcon()
        })
        .catch(error => {
            console.error(error);
            hideLoadingIcon()
        });
    });
});
