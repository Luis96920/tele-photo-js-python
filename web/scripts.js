// scripts.js
$(document).ready(function () {
    const uploadForm = $("#upload-form");
    const imageInput = $("#image-input");
    const originalImage = $("#original-image");
    const processedImage = $("#processed-image");
    const textAboveImages = $("#text-above-images")

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
        const numberDropdown = document.getElementById("number-dropdown");
        const numberValue = numberDropdown.value;
        formData.append("number", numberValue);

        axios.post("https://telephoto.reiform.com/api/upload_and_process", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        })
        .then(response => {
            const imagePairs = response.data;
            for (let i = 0; i < imagePairs.length; i++) {
                const imagePair = imagePairs[i];
                const row = $('<div class="image-row"></div>');
                const caption = $('<div class="caption"></div>').text(imagePair.caption);
                const imagePairDiv = $('<div class="image-pair"></div>');
                const originalImage = $('<img class="original-image">').attr('src', imagePair.original_url);
                const processedImage = $('<img class="processed-image">').attr('src', imagePair.processed_url);
                imagePairDiv.append(originalImage).append(processedImage);
                row.append(caption).append(imagePairDiv);
                $('#image-pairs').append(row);
            }
            hideLoadingIcon();
        })
        .catch(error => {
            console.error(error);
            hideLoadingIcon()
        });
    });
});
