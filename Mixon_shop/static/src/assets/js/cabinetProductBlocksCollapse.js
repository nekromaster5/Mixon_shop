const comparisonLists = document.querySelectorAll('.comparison-list');

// Для каждого блока добавляем обработчик событий на кнопку
comparisonLists.forEach(block => {
    const button = block.querySelector('.fold-button');
    button.addEventListener('click', () => toggleCharacteristicsBlock(block, button));
});

// Функция toggleBlock работает с переданным блоком
function toggleCharacteristicsBlock(block, button) {
    const characteristicsBlocks = block.querySelectorAll('.product__card--characteristics'); // Получаем таблицу заказов
    characteristicsBlocks.forEach(characteristicBlock => {
        const computedStyle = window.getComputedStyle(characteristicBlock);
        if (computedStyle.display === 'none') {
            characteristicBlock.style.display = 'block';
        } else {
            characteristicBlock.style.display = 'none';
        }
    });
    if (button.textContent === 'Развернуть') {
        button.textContent = 'Свернуть';
    } else {
        button.textContent = 'Развернуть';
    }
}