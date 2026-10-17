document.addEventListener('DOMContentLoaded', () => {
    // Инициализация всех слайдеров на странице
    const allSliders = document.querySelectorAll('.slider-container');
    allSliders.forEach(initSlider);
    initMainBannerSlider();
});

/** Main-page banner: navigation, autoplay, keyboard controls and touch swipe. */
function initMainBannerSlider() {
    const root = document.querySelector('.main_image');
    if (!root) return;
    const slides = Array.from(root.querySelectorAll('.main_image_slide'));
    const dots = Array.from(root.querySelectorAll('.main_image_button'));
    const previousButton = root.querySelector('.main_image_arrow--prev');
    const nextButton = root.querySelector('.main_image_arrow--next');
    let currentIndex = 0;
    let autoplayId = null;
    let touchStartX = 0;

    root.dataset.sliderReady = 'true';
    if (!slides.length) { root.hidden = true; return; }

    const show = index => {
        currentIndex = (index + slides.length) % slides.length;
        slides.forEach((slide, slideIndex) => {
            const active = slideIndex === currentIndex;
            slide.classList.toggle('hidden', !active);
            slide.setAttribute('aria-hidden', String(!active));
        });
        dots.forEach((dot, dotIndex) => {
            const active = dotIndex === currentIndex;
            dot.classList.toggle('active', active);
            dot.setAttribute('aria-current', String(active));
        });
    };
    const stopAutoplay = () => {
        if (autoplayId) window.clearInterval(autoplayId);
        autoplayId = null;
    };
    const startAutoplay = () => {
        stopAutoplay();
        if (slides.length < 2 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        autoplayId = window.setInterval(() => show(currentIndex + 1), 5000);
    };
    const select = index => { show(index); startAutoplay(); };

    dots.forEach((dot, index) => dot.addEventListener('click', () => select(index)));
    previousButton?.addEventListener('click', () => select(currentIndex - 1));
    nextButton?.addEventListener('click', () => select(currentIndex + 1));
    root.addEventListener('mouseenter', stopAutoplay);
    root.addEventListener('mouseleave', startAutoplay);
    root.addEventListener('focusin', stopAutoplay);
    root.addEventListener('focusout', startAutoplay);
    root.addEventListener('keydown', event => {
        if (event.key === 'ArrowLeft') select(currentIndex - 1);
        if (event.key === 'ArrowRight') select(currentIndex + 1);
    });
    root.addEventListener('touchstart', event => {
        touchStartX = event.changedTouches[0].clientX;
        stopAutoplay();
    }, {passive: true});
    root.addEventListener('touchend', event => {
        const distance = event.changedTouches[0].clientX - touchStartX;
        if (Math.abs(distance) > 50) show(currentIndex + (distance < 0 ? 1 : -1));
        startAutoplay();
    }, {passive: true});
    show(0);
    startAutoplay();
}

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
