// Находим все кнопки с классом "sort-type"
const sortButtons = document.querySelectorAll('.sort-type');

// Добавляем обработчик события клика для каждой кнопки
sortButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Удаляем класс "active" у всех кнопок
        sortButtons.forEach(btn => btn.classList.remove('active'));
        // Добавляем класс "active" только к нажатой кнопке
        button.classList.add('active');
    });
});