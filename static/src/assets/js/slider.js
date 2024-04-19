document.addEventListener('DOMContentLoaded', () => {
    // Инициализация всех слайдеров на странице
    const allSliders = document.querySelectorAll('.slider-container');
    allSliders.forEach(initSlider);
});

// Определение пользовательского события
const calculateMaxTranslateEvent = new Event('calculateMaxTranslateEvent');

let disableSlider, enableSlider;

function initSlider(sliderContainer) {
    const slider = sliderContainer.querySelector('.slider');
    const slides = sliderContainer.querySelectorAll('.slide');
    let isDragging = false,
        startPos = 0,
        currentTranslate = 0,
        prevTranslate = 0,
        maxTranslate = 0;

    let index = 0;

    const setSliderPosition = () => slider.style.transform = `translateX(${currentTranslate}px)`;

    const getPositionX = e => e.type.includes('touch') ? e.touches[0].clientX : e.clientX;

    const touchStart = (e) => {
        isDragging = true;
        startPos = getPositionX(e);
        prevTranslate = currentTranslate;
        slider.classList.add('grabbing');
    };

    const touchMove = (e) => {
        if (isDragging) {
            const currentPosition = getPositionX(e);
            currentTranslate = prevTranslate + currentPosition - startPos;
            setSliderPosition();
        }
    };

    const touchEnd = () => {
        isDragging = false;
        slider.classList.remove('grabbing');
        if (currentTranslate > 0) {
            currentTranslate = 0;
        } else if (currentTranslate < maxTranslate) {
            currentTranslate = maxTranslate;
        }
        setSliderPosition();
    };

    const calculateMaxTranslate = () => {
        const sliderWidth = slider.offsetWidth;
        setTimeout(() => {
            const totalSlidesWidth = Array.from(slides).reduce((total, slide) => total + slide.offsetWidth + parseInt(window.getComputedStyle(slider).columnGap), 0);
            maxTranslate = sliderWidth - totalSlidesWidth;
            index++;
        }, 270);
    };


    enableSlider = function(slider) {
        // Слушатели событий для сенсорного управления
        slider.addEventListener('touchstart', touchStart);
        slider.addEventListener('touchmove', touchMove);
        slider.addEventListener('touchend', touchEnd);
    };

    disableSlider = function(slider) {
        slider.removeEventListener('touchstart', touchStart);
        slider.removeEventListener('touchmove', touchMove);
        slider.removeEventListener('touchend', touchEnd);
    };

    enableSlider(slider)


    // Инициализируем maxTranslate и добавляем обработчик на изменение размера окна
    calculateMaxTranslate();
    window.addEventListener('resize',() => {
        calculateMaxTranslate();
        currentTranslate = 0;
        setSliderPosition();
    });


    // Функция для вызова calculateMaxTranslate при возникновении события
    function calculateMaxTranslateHandler() {
        calculateMaxTranslate();
    }

    // Добавление слушателя события на document
    document.addEventListener('calculateMaxTranslateEvent', calculateMaxTranslateHandler);


    // Предотвращение появления контекстного меню при долгом нажатии (для тач-устройств)
    slider.oncontextmenu = (event) => {
        event.preventDefault();
        event.stopPropagation();
        return false;
    };
}
