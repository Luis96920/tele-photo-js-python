// scripts.js
$(document).ready(function () {
    const uploadForm = $("#upload-form");
    const imageInput = $("#image-input");
    const countdownTimer = $('#countdown-timer');

    const termsCheckbox = $('#terms');
    const uploadBtn = $('#uploadBtn');

    // Initially disable the button
    uploadBtn.prop('disabled', true);
    uploadBtn.addClass('disabled-btn');

    const fileList = document.getElementById('fileList');
    const fileInput = document.getElementById('image-input');

    fileInput.addEventListener('change', (event) => {
        const files = event.target.files;
  
        // limit the number of files selected to 5
        if (files.length > 5) {
          alert("Please select no more than 5 files.");
          return;
        }
      
        // loop through the selected files and create a FileReader for each
        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          const reader = new FileReader();
      
          // set up the FileReader to display the image on load
          reader.onload = (event) => {
            const imageElement = document.createElement("img");
            imageElement.src = event.target.result;
            fileList.appendChild(imageElement);
          };
      
          // read the file as a data URL
          reader.readAsDataURL(file);
        }
    });

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

    function updateCountdown(secondsLeft) {
        countdownTimer.text(`${secondsLeft} sec`);
      }

    function startTimer(secondsLeft) {
        
        let intervalId = setInterval(function () {
    
            secondsLeft -= 1;

            if (secondsLeft <= 0) {
                secondsLeft = 0;
            }
            
            updateCountdown(secondsLeft);
        }, 1000);
        return intervalId;
    }
      
    function stopTimer(timerInterval) {
    clearInterval(timerInterval);
    }
    

    uploadForm.on("submit", function (event) {
        showLoadingIcon();
        const numberDropdown = document.getElementById("number-dropdown");
        const numberValue = numberDropdown.value;
        updateCountdown(12*parseInt(numberValue));
        timer = startTimer(12 * parseInt(numberValue));
        event.preventDefault();
        const formData = new FormData();
        formData.append("image", imageInput[0].files[0]);
        formData.append("number", numberValue);

        axios.post("https://telephoto.reiform.com/api/upload_and_process", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        })
        .then(async response => {
            const imagePair = response.data;
            
            // Clear the div
            $('#image-pairs').empty();

            const row = $('<div class="image-row"></div>');
            const caption = $('<div class="caption"></div>').text(`=> ${imagePair.caption} =>`);
            const imagePairDiv = $('<div class="image-pair"></div>');
            const originalImage = $('<img class="original-image">').attr('src', imagePair.original_url);
            const processedImage = $('<img class="processed-image">').attr('src', imagePair.processed_url);
            imagePairDiv.append(originalImage).append(processedImage);
            row.append(caption).append(imagePairDiv);
            $('#image-pairs').append(row);

            let processed_url = imagePair.processed_url;
            for (let i = 1; i < parseInt(numberValue); i++) {
                let data = {
                    "url" : processed_url
                }
                try {
                let response = await axios.post("https://telephoto.reiform.com/api/url_and_process", data, {
                    headers: {
                        "Content-Type": "application/json",
                    },
                })
                
                const imagePair = response.data;
                
                // Clear the div
                const row = $('<div class="image-row"></div>');
                const caption = $('<div class="caption"></div>').text(`=> ${imagePair.caption} =>`);
                const imagePairDiv = $('<div class="image-pair"></div>');
                const originalImage = $('<img class="original-image">').attr('src', imagePair.original_url);
                const processedImage = $('<img class="processed-image">').attr('src', imagePair.processed_url);
                imagePairDiv.append(originalImage).append(processedImage);
                row.append(caption).append(imagePairDiv);
                $('#image-pairs').append(row);
                
                processed_url = imagePair.processed_url;
                } catch(error) {
                    console.error(error);
                    hideLoadingIcon();
                    stopTimer(timer);
                }
            }
    
            hideLoadingIcon();
            stopTimer(timer);
        })
        .catch(error => {
            console.error(error);
            hideLoadingIcon();
            stopTimer(timer);
        });

        
    });
});
