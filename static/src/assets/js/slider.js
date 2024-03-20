document.addEventListener('DOMContentLoaded', () => {
    const slider = document.querySelector('.slider');
    const slides = document.querySelectorAll('.slide');
    let isDragging = false,
        startPos = 0,
        currentTranslate = 0,
        prevTranslate = 0,
        maxTranslate = 0;

    const calculateMaxTranslate = () => {
    // Ширина видимого контейнера слайдера
    const sliderContainerWidth = slider.offsetWidth;
    // Ширина всех слайдов с учетом отступов (маржи)
    const totalSlidesWidth = Array.from(slides).reduce((total, slide) => total + slide.offsetWidth, 0);
    // Общий отступ слайдов (например, между слайдами 10px)
    const totalMargin = 10 * (slides.length - 1);
    // Вычисляем maxTranslate, учитывая общий отступ
    maxTranslate = sliderContainerWidth - (totalSlidesWidth + totalMargin);
};


    const setSliderPosition = () => slider.style.transform = `translateX(${currentTranslate}px)`;

    const getPositionX = e => e.type.includes('touch') ? e.touches[0].clientX : e.clientX;

    const animation = () => {
        setSliderPosition();
        if (isDragging) requestAnimationFrame(animation);
    };

    const touchStart = (e) => {
        isDragging = true;
        startPos = getPositionX(e);
        prevTranslate = currentTranslate;
        animation();
    };

    const touchMove = (e) => {
        if (isDragging) {
            const currentPosition = getPositionX(e);
            currentTranslate = prevTranslate + currentPosition - startPos;
        }
    };

    const touchEnd = () => {
        isDragging = false;
        const movedBy = currentTranslate - prevTranslate;

        // Ограничиваем движение слайдера крайними значениями
        if (currentTranslate > 0) {
            currentTranslate = 0;
        } else if (currentTranslate < maxTranslate) {
            currentTranslate = maxTranslate;
        }

        setSliderPosition();
    };

    // Инициализируем maxTranslate при загрузке
    calculateMaxTranslate();
    // Пересчитываем maxTranslate при изменении размера окна, чтобы учесть изменения размера контейнера
    window.addEventListener('resize', calculateMaxTranslate);

    // Добавляем обработчики сенсорных событий
    slider.addEventListener('touchstart', touchStart);
    slider.addEventListener('touchmove', touchMove);
    slider.addEventListener('touchend', touchEnd);


    // Предотвращаем контекстное меню на долгое нажатие
    slider.oncontextmenu = (event) => {
        event.preventDefault();
        event.stopPropagation();
        return false;
    };
});
