document.addEventListener('DOMContentLoaded', function () {
    // Отримуємо елементи
    const lowInput = document.getElementById('filter_price_gte');
    const highInput = document.getElementById('filter_price_lte');
    const lowSlider = document.getElementById('slider-low');
    const highSlider = document.getElementById('slider-high');
    const sliderTrack = document.querySelector('.slider-track');

    // Додаємо елемент для заповнення між повзунками
    const fill = document.createElement('div');
    fill.classList.add('slider-fill');
    sliderTrack.appendChild(fill);

    // Змінні для динамічних меж (будуть оновлюватися з catalogue_filters.js)
    let globalMinPrice = parseInt(lowSlider.getAttribute('min')) || 0;
    let globalMaxPrice = parseInt(highSlider.getAttribute('max')) || 500;

    // Функція для оновлення заповнення між повзунками
    function updateFill() {
        const minVal = parseInt(lowSlider.value);
        const maxVal = parseInt(highSlider.value);
        // Масштабуємо відносно globalMinPrice і globalMaxPrice
        const range = globalMaxPrice - globalMinPrice;
        const minPercent = range ? ((minVal - globalMinPrice) / range) * 100 : 0;
        const maxPercent = range ? ((maxVal - globalMinPrice) / range) * 100 : 100;
        fill.style.left = minPercent + '%';
        fill.style.width = (maxPercent - minPercent) + '%';
    }

    // Функція для оновлення значень
    function updateValues() {
        let lowValue = parseInt(lowSlider.value);
        let highValue = parseInt(highSlider.value);

        // Переконуємося, що лівий повзунок не перевищує правий
        if (lowValue > highValue) {
            lowSlider.value = highValue;
            lowValue = highValue;
        }

        // Переконуємося, що правий повзунок не менший за лівий
        if (highValue < lowValue) {
            highSlider.value = lowValue;
            highValue = lowValue;
        }

        // Оновлюємо поля введення
        lowInput.value = lowValue;
        highInput.value = highValue;

        // Оновлюємо заповнення
        updateFill();
    }

    // Функція для оновлення слайдерів при введенні в поля
    function updateSlidersFromInputs() {
        let lowValue = parseInt(lowInput.value) || globalMinPrice;
        let highValue = parseInt(highInput.value) || globalMaxPrice;

        // Перевірка меж
        if (lowValue < globalMinPrice) {
            lowValue = globalMinPrice;
            lowInput.value = globalMinPrice;
        }
        if (highValue > globalMaxPrice) {
            highValue = globalMaxPrice;
            highInput.value = globalMaxPrice;
        }

        // Переконуємося, що ліве значення не більше правого
        if (lowValue > highValue) {
            lowValue = highValue;
            lowInput.value = highValue;
        }
        if (highValue < lowValue) {
            highValue = lowValue;
            highInput.value = lowValue;
        }

        // Оновлюємо слайдери
        lowSlider.value = lowValue;
        highSlider.value = highValue;

        // Оновлюємо заповнення
        updateFill();
    }

    // Додаємо обробники подій для слайдерів
    lowSlider.addEventListener('input', updateValues);
    highSlider.addEventListener('input', updateValues);

    // Додаємо обробники подій для полів введення
    lowInput.addEventListener('input', updateSlidersFromInputs);
    highInput.addEventListener('input', updateSlidersFromInputs);

    // Ініціалізація
    updateValues();

    // Експортуємо функції для використання в catalogue_filters.js
    window.sliderUtils = {
        updateFill: updateFill,
        setGlobalMinPrice: (value) => {
            globalMinPrice = value;
        },
        setGlobalMaxPrice: (value) => {
            globalMaxPrice = value;
        },
    };
});