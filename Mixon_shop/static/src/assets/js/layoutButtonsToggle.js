// Находим все кнопки с классом "layout-style"
const layoutButtons = document.querySelectorAll('.layout-style');

// Добавляем обработчик события клика для каждой кнопки
layoutButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Удаляем класс "active" у всех кнопок
        layoutButtons.forEach(btn => btn.classList.remove('active'));
        // Добавляем класс "active" только к нажатой кнопке
        button.classList.add('active');
    });
});