const buttons = document.querySelectorAll('.widget__cabinet--button');

// Добавляем обработчик события клика для каждой кнопки
buttons.forEach(button => {
    button.addEventListener('click', () => {
        // Удаляем класс "active" у всех кнопок
        buttons.forEach(btn => btn.classList.remove('active'));
        // Добавляем класс "active" только к нажатой кнопке
        button.classList.add('active');
    });
});