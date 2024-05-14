// Находим все блоки на странице с классом review_personal_block
const reviewBlocks = document.querySelectorAll('.review_personal_block');

// Для каждого блока добавляем обработчик событий на кнопку
reviewBlocks.forEach(block => {
    const button = block.querySelector('.order_button');
    button.addEventListener('click', () => toggleReviewBlock(block));
});

// Функция toggleBlock работает с переданным блоком
function toggleReviewBlock(block) {
    const table = block.querySelector('.open_order_bord'); // Получаем таблицу заказов
    const text = block.querySelector('.button_text'); // Получаем кнопку

    const computedStyle = window.getComputedStyle(table);
    if (computedStyle.display === 'none') {
        table.style.display = 'block';
        text.textContent = 'Свернуть >>'; // Текст при открытом состоянии
    } else {
        table.style.display = 'none';
        text.textContent = 'Детально >>'; // Текст при закрытом состоянии
    }
}