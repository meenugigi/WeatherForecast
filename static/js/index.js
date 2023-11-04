document.addEventListener("DOMContentLoaded", function() {
    let isPopupOpen = false;
    // create a custom popup window on clicking each weather forecast card
    function openPopupWindow(card) {
    // if window already open, indicate user to close popup to open another popup window
    // if user attempts to open new window with another window open, span size of open window
    // to indicate user to close it before opening another window.
        if(isPopupOpen) {
        const closeButtons = card.querySelectorAll(".popup");
                closeButtons.forEach((closeButton) => {
                    closeButton.classList.add("enlarged");
                    setTimeout(() => {
                        closeButton.classList.remove("enlarged");
                    }, 150);
                });
            return;
        }
        isPopupOpen = true;
        card.querySelector(".popup").style.display = "flex";
    }

    // Event listeners to open popups for each card
    const forecastCards = document.querySelectorAll(".card");
    forecastCards.forEach((card) => {
        card.addEventListener("click", function() {
            openPopupWindow(this);
        });
    });

    // To close popup windows
    const closeButtons = document.querySelectorAll(".close");
    closeButtons.forEach((closeButton) => {
        closeButton.addEventListener("click", function (e) {
            e.stopPropagation();
            this.closest(".popup").style.display = "none";
            isPopupOpen = false;
      });
    });


    // to display error warnings if user enters a value greater than 3
    // or less than 1 for 'days' field on input form.
    const numDaysInput = document.getElementById("num_days");
    const errorMessage = document.getElementById("error_message");

    numDaysInput.addEventListener("input", function() {
        const value = this.value;

        if (!/^\d+$/.test(value) || parseInt(value) >= 4 || parseInt(value) <= 0 ) {
            errorMessage.textContent = "Please enter a valid number between 0 and 4.";
            this.setCustomValidity("Invalid input");
        } else {
            errorMessage.textContent = "";
            this.setCustomValidity("");
        }
    });







});