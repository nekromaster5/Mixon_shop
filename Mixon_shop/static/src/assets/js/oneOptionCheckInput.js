const circleCheckBoxes = document.querySelectorAll('.only-one')
circleCheckBoxes.forEach(circleCheckBox => {
    const checkboxes = circleCheckBox.querySelectorAll('.widget__form--check__input');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            if (this.checked) {
                checkboxes.forEach(otherCheckbox => {
                    if (otherCheckbox !== this) {
                        otherCheckbox.checked = false;
                    }
                });
            }
        });
    });
});