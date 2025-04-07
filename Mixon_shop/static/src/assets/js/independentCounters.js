// Делаем updateTotalPrice глобальной функцией, возвращающей Promise
window.updateTotalPrice = async function updateTotalPrice() {
    const productsData = {};
    document.querySelectorAll('.product--amount__input').forEach(input => {
        const productId = input.closest('.cart__product--value').dataset.productId;
        productsData[productId] = input.value;
    });


    const response = await fetch('/checkout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ products: productsData })
    });

    if (!response.ok) {
        throw new Error('Ошибка сети: ' + response.status);
    }

    const data = await response.json();

    const totalPrice = typeof data.total_price === 'string' ? parseFloat(data.total_price.replace(',', '.')) : data.total_price;

    if (isNaN(totalPrice)) {
        console.error('total_price не является числом:', data.total_price);
        return 0;
    }

    const newTotalPrice = totalPrice.toFixed(2).replace('.', ',') + '₴';
    const totalElements = document.querySelectorAll('.checkout-total');
    totalElements.forEach(element => {
        element.textContent = newTotalPrice;
    });

    window.currentTotalPrice = totalPrice;
    return totalPrice; // Возвращаем сумму
};

function adjustCounter(input, increase) {
    let value = parseInt(input.value, 10);
    value = isNaN(value) ? 1 : increase ? value + 1 : Math.max(1, value - 1);
    input.value = value;
    updatePrice(input);
    updateTotalPrice().then(() => {
        // После пересчета общей суммы вызываем applyDiscount из promo.js
        if (typeof window.applyDiscount === 'function') {
            window.applyDiscount();
        }
    });
    updateConfirmOrder(input);
}

function updatePrice(input) {
    const counter = input.closest('.product--amount');
    const productContainer = counter.closest('.cart__product--value');
    const priceElement = productContainer.querySelector('.cart__price');
    const oldPriceElement = productContainer.querySelector('.cart__price--old');

    const basePrice = parseFloat(priceElement.getAttribute('data-base-price'));
    const count = parseInt(input.value, 10);
    priceElement.textContent = (basePrice * count).toFixed(2).replace('.', ',');

    if (oldPriceElement) {
        const baseOldPrice = parseFloat(oldPriceElement.getAttribute('data-base-price'));
        oldPriceElement.textContent = (baseOldPrice * count).toFixed(2).replace('.', ',');
    }
}

function updateConfirmOrder(input) {
    const productContainer = input.closest('.cart__product--value');
    const index = productContainer.dataset.index;
    const count = parseInt(input.value, 10);

    const confirmAmountElement = document.querySelector(`.product-amount-confirm[data-index="${index}"]`);
    const confirmPriceElement = document.querySelector(`.product-price-confirm[data-index="${index}"]`);

    if (confirmAmountElement) {
        confirmAmountElement.textContent = count;
    }

    if (confirmPriceElement) {
        const basePrice = parseFloat(productContainer.querySelector('.cart__price').getAttribute('data-base-price'));
        const newPrice = (basePrice * count).toFixed(2).replace('.', ',') + '₴';
        confirmPriceElement.textContent = newPrice;
    }
}

function getCsrfToken() {
    const name = 'csrftoken';
    const cookieValue = document.cookie.split('; ')
        .find(row => row.startsWith(name))
        ?.split('=')[1];
    return cookieValue || '';
}

// Обработчики для счетчиков
document.querySelectorAll('.product--amount').forEach(counter => {
    const numberInput = counter.querySelector('.product--amount__input');
    const priceElement = counter.closest('.cart__product--value').querySelector('.cart__price');
    const oldPriceElement = counter.closest('.cart__product--value').querySelector('.cart__price--old');

    priceElement.setAttribute('data-base-price', parseFloat(priceElement.textContent.replace(',', '.')));
    if (oldPriceElement) {
        oldPriceElement.setAttribute('data-base-price', parseFloat(oldPriceElement.textContent.replace(',', '.')));
    }

    counter.querySelector('.increase').addEventListener('click', () => {
        adjustCounter(numberInput, true);
    });
    counter.querySelector('.decrease').addEventListener('click', () => {
        adjustCounter(numberInput, false);
    });

    numberInput.addEventListener('change', () => {
        let value = parseInt(numberInput.value, 10);
        numberInput.value = isNaN(value) || value < 1 ? 1 : value;
        updatePrice(numberInput);
        updateTotalPrice().then(() => {
            if (typeof window.applyDiscount === 'function') {
                window.applyDiscount();
            }
        });
        updateConfirmOrder(numberInput);
    });
});

// Инициализация таблицы подтверждения при загрузке
document.querySelectorAll('.product--amount__input').forEach(input => {
    updateConfirmOrder(input);
});