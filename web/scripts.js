// scripts.js
$(document).ready(function () {
    const uploadForm = $("#upload-form");
    const countdownTimer = $("#countdown-timer");
    
    const imageInput = $("#image-input");
    const versionCheckbox = document.getElementById('version');

    const fileList = document.getElementById('fileList');
    const fileListSingle = document.getElementById('fileListSingle');
    const fileInput = document.getElementById('image-input');

    const dropdownContainer = document.getElementById('dropdown-container');
    const subjectContainer = document.getElementById('subject-container');

    fileInput.addEventListener('change', (event) => {
        const files = event.target.files;
        
        // limit the number of files selected to 5
        if (files.length > 5) {
          alert("Please select no more than 5 files.");
          return;
        }
        
        $("#fileList").empty();
        $("#fileListSingle").empty();
        
        let fileContainer = fileList
        if (versionCheckbox.checked) {
            fileContainer = fileListSingle
        }

        // loop through the selected files and create a FileReader for each
        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          const reader = new FileReader();
      
          // set up the FileReader to display the image on load
          reader.onload = (event) => {
            const imageElement = document.createElement("img");
            imageElement.src = event.target.result;
            fileContainer.appendChild(imageElement);
          };
      
          // read the file as a data URL
          reader.readAsDataURL(file);
        }

    });

    versionCheckbox.addEventListener("change", (event) => {
        if (event.target.checked) {
            fileInput.removeAttribute("multiple");
            fileInput.removeAttribute("name");
            dropdownContainer.style.display = '';
            subjectContainer.style.display = 'none';
            $("#fileList").empty();
        } else {
            fileInput.setAttribute("multiple", "");
            fileInput.setAttribute("name", "images[]");
            dropdownContainer.style.display = 'none';
            subjectContainer.style.display = '';
            $("#fileListSingle").empty();
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

    const downloadAllButton = document.getElementById('download-all');

    downloadAllButton.addEventListener('click', () => {
        fileURLs.forEach((fileUrl) => {
            const link = document.createElement('a');
            link.href = fileUrl;
            link.download = fileUrl.split('/').pop();
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    });
    
    let fileURLs = []

    uploadForm.on("submit", function (event) {
        showLoadingIcon();
        const numberDropdown = document.getElementById("number-dropdown");
        let numberValue = parseInt(numberDropdown.value);
        const formData = new FormData();
        if (!versionCheckbox.checked) {
            numberValue = 1;
            updateCountdown(fileInput.files.length * 11);
            timer = startTimer(fileInput.files.length * 11);
            const labelField = document.getElementById("class-keyword");
            for (let i = 0; i < Math.min(fileInput.files.length, 5); i++) {
                formData.append('images[]', fileInput.files[i]);
            }
            formData.append("description", labelField.value);
        } else {
            updateCountdown(12*numberValue);
            timer = startTimer(12 * numberValue);
            formData.append("image", imageInput[0].files[0]);
        }

        event.preventDefault();

        fileURLs = []

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
            const processedImage = $('<img class="processed-image">').attr('src', imagePair.processed_url);
            imagePairDiv.append(processedImage);
            row.append(caption).append(imagePairDiv);
            $('#image-pairs').append(row);

            
            let processed_url = imagePair.processed_url;
            fileURLs = [processed_url]
            for (let i = 1; i < numberValue; i++) {
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
                const processedImage = $('<img class="processed-image">').attr('src', imagePair.processed_url);
                const downloadButton = $(`<a href="${imagePair.processed_url}" download="generate-image.png">Download Image</a>`)
                imagePairDiv.append(processedImage);
                imagePairDiv.append(downloadButton);
                row.append(caption).append(imagePairDiv);
                $('#image-pairs').append(row);
                
                processed_url = imagePair.processed_url;
                fileURLs.push(processed_url)
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
