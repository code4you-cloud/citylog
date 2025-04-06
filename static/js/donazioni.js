document.addEventListener("DOMContentLoaded", function () {
    const donateButtons = document.querySelectorAll(".donate-btn");
    const customAmountInput = document.getElementById("custom-amount");

    donateButtons.forEach(button => {
        button.addEventListener("click", function () {
            const amount = this.getAttribute("data-amount");
            customAmountInput.value = amount;
        });
    });
});

