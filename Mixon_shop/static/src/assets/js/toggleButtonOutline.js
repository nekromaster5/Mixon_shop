document.addEventListener('DOMContentLoaded', function () {
    // Получаем все кнопки по классу
    const shipmentLists = document.querySelectorAll('.shipment--types__list');
    shipmentLists.forEach(initShipmentButtons);
});

function initShipmentButtons(shipmentList) {
    const buttons = shipmentList.querySelectorAll('.shipment__page--list--item');

    // Функция для удаления стилей у всех кнопок, кроме активной
    const removeStyles = (activeElement) => {
        buttons.forEach(button => {
            if (button !== activeElement) {
                button.style.border = ''; // Убираем красный контур
                button.style.boxShadow = ''; // Убираем тень
                button.classList.remove('active'); // Убираем класс active
            }
        });
    };

    // Добавляем каждой кнопке обработчик события на клик
    buttons.forEach(button => {
        button.addEventListener('click', function () {
            removeStyles(this); // Удаляем стили у всех кнопок, кроме текущей
            this.style.border = '1.5px solid rgb(255, 0, 0)'; // Добавляем красный контур текущей кнопке
            this.style.boxShadow = '5px 5px 10px rgba(174, 173, 170, 0.5), -5px 5px 10px rgba(174, 173, 170, 0.5), 0px 10px 10px rgba(174, 173, 170, 0.5)';
            this.classList.add('active'); // Добавляем класс "active" текущей кнопке
        });
    });
}
