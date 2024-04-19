document.addEventListener('DOMContentLoaded', function() {
    const scrollButtons = document.querySelectorAll('.checkout--next__action--btn');
    scrollButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetBlock = document.getElementById(targetId);
            if (targetBlock) {
                targetBlock.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});