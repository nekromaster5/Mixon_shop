// // Функция увеличения и уменьшения значения счетчика
// function adjustCounter(input, increase) {
//   let value = parseInt(input.value, 10);
//   value = isNaN(value) ? 1 : increase ? value + 1 : Math.max(1, value - 1);
//   input.value = value;
// }
//
// // Назначаем обработчики для каждой кнопки в каждом счетчике
// document.querySelectorAll('.product--amount').forEach(counter => {
//   const numberInput = counter.querySelector('.product--amount__input');
//
//   counter.querySelector('#increase').addEventListener('click', () => adjustCounter(numberInput, true));
//   counter.querySelector('#decrease').addEventListener('click', () => adjustCounter(numberInput, false));
//
//   numberInput.addEventListener('change', () => {
//     let value = parseInt(numberInput.value, 10);
//     numberInput.value = isNaN(value) || value < 1 ? 1 : value;
//   });
// });


function adjustCounter(input, increase) {
    let value = parseInt(input.value, 10);
    value = isNaN(value) ? 1 : increase ? value + 1 : Math.max(1, value - 1);
    input.value = value;
    updatePrice(input);
    updateTotalPrice();
    updateConfirmOrder(input);
}

function updatePrice(input) {
    const counterContainer = input.closest('.cart__product--value');
    const priceElement = counterContainer.querySelector('.cart__price');
    const oldPriceElement = counterContainer.querySelector('.cart__price--old');

    const basePrice = parseFloat(priceElement.getAttribute('data-base-price'));
    const baseOldPrice = oldPriceElement ? parseFloat(oldPriceElement.getAttribute('data-base-price')) : null;

    let quantity = parseInt(input.value, 10);

    if (!isNaN(basePrice)) {
        priceElement.textContent = (basePrice * quantity).toFixed(2).replace('.', ',') + '₴';
    }
    if (baseOldPrice !== null && !isNaN(baseOldPrice)) {
        oldPriceElement.textContent = (baseOldPrice * quantity).toFixed(2).replace('.', ',') + '₴';
    }
}

function updateTotalPrice() {
    let totalPrice = 0;
    document.querySelectorAll('.cart__price').forEach(priceElement => {
        totalPrice += parseFloat(priceElement.textContent.replace(',', '.').replace('₴', '')) || 0;
    });

    document.querySelectorAll('.checkout-total').forEach(totalElement => {
        totalElement.textContent = totalPrice.toFixed(2).replace('.', ',') + '₴';
    });
}

function updateConfirmOrder(input) {
    let index = input.getAttribute('data-index');
    let quantity = parseInt(input.value, 10);
    let priceElement = document.querySelector(`.cart__price[data-index='${index}']`);
    let basePrice = parseFloat(priceElement.getAttribute('data-base-price'));
    let finalPrice = (basePrice * quantity).toFixed(2).replace('.', ',') + '₴';

    document.querySelector(`.product-amount-confirm[data-index='${index}']`).textContent = quantity;
    document.querySelector(`.product-price-confirm[data-index='${index}']`).textContent = finalPrice;
}

// Назначаем обработчики для каждой кнопки в каждом счетчике

document.querySelectorAll('.product--amount').forEach(counter => {
    const numberInput = counter.querySelector('.product--amount__input');
    const priceElement = counter.closest('.cart__product--value').querySelector('.cart__price');
    const oldPriceElement = counter.closest('.cart__product--value').querySelector('.cart__price--old');

    // Сохраняем базовые цены в data-атрибутах
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
        updateTotalPrice();
        updateConfirmOrder(numberInput);
    });
});
