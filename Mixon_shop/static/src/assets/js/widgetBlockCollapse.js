// Знаходимо всі блоки на сторінці з класом single__widget
const widgetBlocks = document.querySelectorAll('.single__widget');

// Для кожного блоку додаємо обробник подій на заголовок
widgetBlocks.forEach(block => {
    const title = block.querySelector('.widget__title');
    title.addEventListener('click', () => toggleFormVisibility(block));
});

// Функція toggleFormVisibility працює з переданим блоком
function toggleFormVisibility(block) {
    const content = block.querySelector('.widget__content'); // Отримуємо форму
    const arrow = block.querySelector('.arrow_image');
    if (content.style.display === 'none') {
        content.style.display = 'block'; // Робимо форму видимою
        arrow.classList.remove('inactive')
    } else {
        content.style.display = 'none'; // Робимо форму невидимою
        arrow.classList.add('inactive')
    }
}