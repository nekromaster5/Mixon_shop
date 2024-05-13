document.addEventListener('DOMContentLoaded', function () {
    const scrollButtons = document.querySelectorAll('.checkout--next__action--btn');
    scrollButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const targetBlock = document.getElementById(targetId);
            if (targetBlock) {
                const headerHeight = 71; // Высота вашего стики хедера
                const targetPosition = targetBlock.getBoundingClientRect().top + window.scrollY - headerHeight;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});