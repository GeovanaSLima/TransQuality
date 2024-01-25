let currentQuestionIndex = 0;
const questionEl = document.getElementById("question");
const questionIndexEl = document.getElementById("question-index");
const questionThemaEl = document.getElementById("theme");
const questionLocaliEl = document.getElementById("location");
const answerEl = document.getElementById("answer");
const reservesEl = document.getElementById("reserves");
const nextBtn = $('#next-btn');
const saveBtn = $('#save-btn');
const avecRadio = document.getElementById("With Reservations");
const sansRadio = document.getElementById("Without Reservations");
const enregiBtn = document.getElementById("save-confirm-btn");
const backBtn = document.getElementById("back-btn");
const imageInput = document.getElementById("image-upload");
const imagePreview = document.getElementById("image-preview");
const imagePreviewContainer = document.getElementById("image-preview-container");
const savePdfBtn = document.getElementById("save-confirm-pdf-btn");
let formId = parseInt(document.getElementById('form-id').value);
var questionIndex = parseInt(questionIndexEl.textContent.slice(-1));
let lastQuestionIndex = 0;
let responses = JSON.parse(localStorage.getItem('responses')) || [];


///////////////////////////////////// QUESTIONNAIRE /////////////////////////////////////


$(document).ready(function () {
    var lastQuestionIndex = questionIndex - 1;

    // Show the appropriate buttons based on the current question index
    if (questionIndex === 1) {
        $('#next-btn').show();
    } else if (questionIndex === lastQuestionIndex) {
        $('#back-btn').show();
        $('#save-btn').show();
    } else {
        $('#back-btn').show();
        $('#next-btn').show();
    }

    if (avecRadio.checked) {
        showAdditionalOptions();
    }

});

saveBtn.click(function () {
    if (isFormValid()) {
        $("#confirmModal").modal("show");
    }
});

nextBtn.click(function () {
    if (isFormValid()) {
        var questionDestination = questionIndex + 1;
        var Destination = '/questionnaire/' + formId + '/' + questionDestination;

        saveResponse(Destination);
    }
});

backBtn.addEventListener("click", function (event) {
    event.preventDefault();
    if (isFormValid()) {
        var questionDestination = questionIndex - 1;
        var destination = '/questionnaire/' + formId + '/' + questionDestination;

        // Save the current response before navigating to the previous question
        saveResponse(destination);
    }
});


imageInput.addEventListener("change", previewImage);


enregiBtn.addEventListener("click", function () {
    var destinationHome = '/home';
    saveResponse(destinationHome);
});


savePdfBtn.addEventListener("click", function () {
    var destinationHomePdf = '/home';
    saveResponseAndGeneratePDF(destinationHomePdf);
  }); 


function populateFormFields(index) {
    $('input[name="answer"]').filter(`[value="${index.response}"]`).prop('checked', true);

    if (!index) {
        return;
    }

    if (index.reserve === '') {
        sansRadio.checked = true;
    } else {
        $('input[name="reserve"]').filter(`[value="${index.reserve}"]`).prop('checked', true);
        avecRadio.checked = true;
    }

    // Set the observation
    $('#observation').val(index.observation);

    // Set the image preview
    if (index.image) {
        imagePreviewContainer.style.display = "block";
        imagePreview.src = index.image;
    }
}


function getResponseByQuestionNumber(number) {
    return responses.find(
        (response) => response.question_number === number
    ) || null;
}


function showAdditionalOptions() {
    var avecRadio = document.getElementById("With Reservations");
    var reservesEl = document.getElementById("reserves");
    var observationEl = document.getElementById("observation");

    if (avecRadio.checked) {
        reservesEl.style.display = "block";
        observationEl.setAttribute("required", "");
    } else {
        reservesEl.style.display = "none";
        observationEl.removeAttribute("required");
    }
}


function isFormValid() {
    var avecRadio = document.getElementById("With Reservations");
    var observationEl = document.getElementById("observation");
    var observationValue = observationEl.value.trim();
    var reserveOptions = document.getElementsByName("reserve");
    var reserveSelected = false;
    var answerOptions = document.getElementsByName("answer");
    var answerSelected = false;

    for (var i = 0; i < reserveOptions.length; i++) {
        if (reserveOptions[i].checked) {
            reserveSelected = true;
            break;
        }
    }

    for (var i = 0; i < answerOptions.length; i++) {
        if (answerOptions[i].checked) {
            answerSelected = true;
            break;
        }
    }

    if (!answerSelected) {
        alert("Please select an answer.");
        return false;
    }

    if (avecRadio.checked && observationValue.length < 2) {
        alert("Observation must be at least 1 character long.");
        return false;
    }

    if (avecRadio.checked && !reserveSelected) {
        alert("Please select a reserve option.");
        return false;
    }

    return true;
}


function previewImage(event) {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function () {
        const imageUrl = reader.result;
        imagePreview.src = imageUrl;
        imagePreviewContainer.style.display = "block";
    };

    reader.readAsDataURL(file);
}


function generateRandomFilename(fileType) {
    const characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    const length = 10;
    let randomFilename = '';
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        randomFilename += characters.charAt(randomIndex);
    }
    return randomFilename + '.' + fileType;
}


function uploadFiles() {
    const files = imageInput.files;
    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileType = file.name.split('.').pop();
        // const randomFilename = generateRandomFilename(fileType);
        formData.append('files', file, fileType);
    }

    const formIdValue = parseInt(formId); // Rename the local variable

    // Rename the local variable from 'questionIndex' to 'questionIndexValue'
    const questionIndexValue = parseInt(questionIndex);

    fetch(`/upload-files/${formIdValue}/${questionIndexValue}`, {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const images = data.images;

            console.log(images);

            const imageUrl = images[0];
            imagePreview.src = imageUrl;
            imagePreviewContainer.style.display = "block";

            // Update the response object with the image URL
            const currentResponse = getResponseByQuestionNumber(questionIndexValue);
            if (currentResponse) {
                currentResponse.image = imageUrl;
                localStorage.setItem('responses', JSON.stringify(responses));
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function openPDF() {
    window.open("/generate-pdf/" + formId, "_blank");
}


// Function to generate the PDF and redirect the user
function generatePDFAndRedirect() {
    fetch(`/generate-pdf/${parseInt(formId)}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response;
        })
        // .then(blob => {
        //     const pdfUrl = URL.createObjectURL(blob);
        //     window.open(pdfUrl, "_blank");

        // Redirect the user to the home page
        // window.location.href = "/home";
        // })
        .catch(error => {
            console.error("There was a problem with the fetch operation:", error);
        });
}

// Function to save the response and trigger PDF generation
function saveResponseAndGeneratePDF(redirectDestination) {
    const selectedAnswer = $('input[name="answer"]:checked').val();

    let reserveOption = '';
    if (sansRadio.checked) {
        reserveOption = '';
    } else {
        reserveOption = $('input[name="reserve"]:checked').val();
    }

    const observation = $('#observation').val().trim();

    // Check if imagePreview.src is not an empty string
    let imageSrc = "";
    if (imagePreview && imagePreview.src !== "") {
        let url = imagePreview.src;
        let staticIndex = url.indexOf("static");
        imageSrc = url.slice(staticIndex);
    }

    const responseObj = {
        "form_id": formId,
        "user_id": "",
        "question_number": questionIndex,
        "answer": selectedAnswer,
        "reserve": reserveOption,
        "observation": observation,
        "image": imageSrc
    };

    fetch("/save_responses", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(responseObj)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            if (data.success) {
                responseObj.image = data.url; // Update the response object with the URL
                localStorage.removeItem("formResponses");
                uploadFiles();
                openPDF(); // Call the function to generate the PDF and open it
                window.location.href = redirectDestination;
            } else {
                alert("There was an error saving the responses. Please try again.");
            }
        })
        .catch(error => {
            console.error("There was a problem with the fetch operation:", error);
        });

    console.log('Response saved:', responseObj);

    localStorage.setItem('responses', JSON.stringify(responses));
}



function saveResponse(redirectDestination) {
    const selectedAnswer = $('input[name="answer"]:checked').val();

    let reserveOption = '';
    if (sansRadio.checked) {
        reserveOption = '';
    } else {
        reserveOption = $('input[name="reserve"]:checked').val();
    }

    const observation = $('#observation').val().trim();

    // Check if imagePreview.src is not an empty string
    let imageSrc = "";
    if (imagePreview && imagePreview.src !== "") {
        let url = imagePreview.src;
        let staticIndex = url.indexOf("static");
        imageSrc = url.slice(staticIndex);
    }

    const responseObj = {
        "form_id": formId, // Use the global formId variable
        "question_number": questionIndex,
        "answer": selectedAnswer,
        "reserve": reserveOption,
        "observation": observation,
        "image": imageSrc
    };

    fetch("/save_responses", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(responseObj)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            if (data.success) {
                localStorage.removeItem("formResponses");
                window.location.href = redirectDestination;

                // Call uploadFiles to save the images
                uploadFiles(); // Assuming you want to upload files
            } else {
                alert("There was an error saving the responses. Please try again.");
            }
        })
        .catch(error => {
            console.error("There was a problem with the fetch operation:", error);
        });

    console.log('Response saved:', responseObj);

    localStorage.setItem('responses', JSON.stringify(responses));
}