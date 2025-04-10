document.addEventListener('DOMContentLoaded', function () {
    // Функція для генерації зірок для одного контейнера
    function generateStars(container) {
        // Перевіряємо, чи контейнер уже оброблений
        if (container.classList.contains('processed')) {
            return;
        }

        // Отримуємо рейтинг і замінюємо кому на крапку
        const rawRating = container.getAttribute('data-rating') || '0';
        const rating = parseFloat(rawRating.replace(',', '.')) || 0;

        // Обчислюємо цілу та дробову частини
        const wholePart = Math.floor(rating);
        const fraction = rating - wholePart;

        // Очищаємо контейнер
        container.innerHTML = '';

        // Генеруємо 5 зірок
        for (let i = 1; i <= 5; i++) {
            const listItem = document.createElement('li');
            listItem.className = 'rating__list';
            const span = document.createElement('span');
            span.className = 'rating__icon';

            // Створюємо SVG
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('width', '19');
            svg.setAttribute('height', '19');
            svg.setAttribute('viewBox', '0 0 19 19');
            svg.setAttribute('fill', 'none');

            if (i <= wholePart) {
                // Повна золота зірка
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.setAttribute('d', 'M9.16723 0L11.9997 5.93799L18.3325 6.89001L13.7499 11.512L14.8313 18.0389L9.16625 14.957L3.50124 18.0389L4.58265 11.512L0 6.89001L6.33277 5.93799L9.16723 0Z');
                path.setAttribute('fill', '#FFC107');
                svg.appendChild(path);
            } else if (i === wholePart + 1 && fraction > 0.01) {
                // Частково заповнена зірка з градієнтом
                const percentage = fraction * 100;

                // Створюємо градієнт
                const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
                const linearGradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
                linearGradient.setAttribute('id', `grad-${i}-${container.dataset.rating.replace(',', '-')}-${Math.random().toString(36).substr(2, 9)}`); // Унікальний ID
                linearGradient.setAttribute('x1', '0%');
                linearGradient.setAttribute('y1', '0%');
                linearGradient.setAttribute('x2', '100%');
                linearGradient.setAttribute('y2', '0%');

                // Створюємо stop для золотого кольору (зліва)
                const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
                stop1.setAttribute('offset', `${percentage}%`);
                stop1.setAttribute('style', 'stop-color:#FFC107;stop-opacity:1');
                linearGradient.appendChild(stop1);

                // Створюємо stop для сірого кольору (справа)
                const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
                stop2.setAttribute('offset', `${percentage}%`);
                stop2.setAttribute('style', 'stop-color:#AEADAA;stop-opacity:1');
                linearGradient.appendChild(stop2);

                defs.appendChild(linearGradient);
                svg.appendChild(defs);

                // Додаємо зірку з градієнтом
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.setAttribute('d', 'M9.16723 0L11.9997 5.93799L18.3325 6.89001L13.7499 11.512L14.8313 18.0389L9.16625 14.957L3.50124 18.0389L4.58265 11.512L0 6.89001L6.33277 5.93799L9.16723 0Z');
                path.setAttribute('fill', `url(#${linearGradient.getAttribute('id')})`);
                svg.appendChild(path);
            } else {
                // Порожня сіра зірка
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.setAttribute('d', 'M9.16723 0L11.9997 5.93799L18.3325 6.89001L13.7499 11.512L14.8313 18.0389L9.16625 14.957L3.50124 18.0389L4.58265 11.512L0 6.89001L6.33277 5.93799L9.16723 0Z');
                path.setAttribute('fill', '#AEADAA');
                svg.appendChild(path);
            }

            span.appendChild(svg);
            listItem.appendChild(span);
            container.appendChild(listItem);
        }

        // Позначимо контейнер як оброблений
        container.classList.add('processed');
    }

    // Обробляємо всі існуючі елементи при завантаженні сторінки
    const initialRatings = document.querySelectorAll('.rating');
    initialRatings.forEach(generateStars);

    // Налаштовуємо MutationObserver для відстеження змін у DOM
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            // Перевіряємо додані вузли
            mutation.addedNodes.forEach(node => {
                // Якщо це елемент і він має клас .rating
                if (node.nodeType === Node.ELEMENT_NODE && node.classList && node.classList.contains('rating')) {
                    generateStars(node);
                }
                // Якщо це контейнер, шукаємо всередині нього елементи .rating
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const newRatings = node.querySelectorAll('.rating');
                    newRatings.forEach(generateStars);
                }
            });
        });
    });

    // Налаштовуємо параметри MutationObserver
    const observerConfig = {
        childList: true, // Відстежуємо додавання/видалення дочірніх елементів
        subtree: true, // Відстежуємо зміни у всьому піддереві
    };

    // Починаємо спостерігати за document.body
    observer.observe(document.body, observerConfig);
});