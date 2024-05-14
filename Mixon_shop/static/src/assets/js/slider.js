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
        const sliderContainerWidth = sliderContainer.offsetWidth;
        if (sliderContainer.classList.contains('adjustable-slider')) {
            let totalSlidesWidth;
            setTimeout(() => {
                totalSlidesWidth = Array.from(slides).reduce((total, slide) => total + slide.offsetWidth
                    + getMarginAndPaddingSum(slide) + getGap() + 10, 0);
                maxTranslate = sliderContainerWidth - totalSlidesWidth;
                index++;
            }, 270);
        } else {
            const sliderWidth = slider.offsetWidth;
            maxTranslate = sliderContainerWidth - sliderWidth;
        }
    };

    function getGap() {
        let columnGap = parseFloat(window.getComputedStyle(slider).columnGap);
        if (columnGap) {
            return columnGap
        }
        return 0
    }

    function getMarginAndPaddingSum(element) {
        if (!element) {
            console.error("Element not found");
            return;
        }

        const computedStyle = window.getComputedStyle(element);
        const margin = parseFloat(computedStyle.marginLeft) + parseFloat(computedStyle.marginRight);
        const padding = parseFloat(computedStyle.paddingLeft) + parseFloat(computedStyle.paddingRight);

        return margin + padding;
    }

    enableSlider = function (slider) {
        // Слушатели событий для сенсорного управления
        slider.addEventListener('touchstart', touchStart);
        slider.addEventListener('touchmove', touchMove);
        slider.addEventListener('touchend', touchEnd);
    };

    disableSlider = function (slider) {
        slider.removeEventListener('touchstart', touchStart);
        slider.removeEventListener('touchmove', touchMove);
        slider.removeEventListener('touchend', touchEnd);
    };

    enableSlider(slider)


    // Инициализируем maxTranslate и добавляем обработчик на изменение размера окна
    calculateMaxTranslate();
    window.addEventListener('resize', () => {
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
