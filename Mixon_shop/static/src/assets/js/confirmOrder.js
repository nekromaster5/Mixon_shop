document.addEventListener("DOMContentLoaded", function () {
    document.querySelector("#confirmation--next__action").addEventListener("click", async function (e) {
        e.preventDefault();

        const name = document.querySelector('#input_name').value.trim();
        const phone = document.querySelector('#input_phone').value.trim();
        const email = document.querySelector('#input_email').value.trim();

        const shipmentMethodButton = document.querySelector('.shipment__page--list--item.shipping.active');
        if (!shipmentMethodButton) {
            alert("Пожалуйста, выберите способ доставки.");
            return;
        }
        const shipmentMethodId = shipmentMethodButton.dataset.id;
        const shipmentCost = 0;

        const selectedBranch = document.querySelector('.widget__form--check__input:checked');
        if (!selectedBranch) {
            alert("Пожалуйста, выберите филиал для доставки.");
            return;
        }
        const orderPlaceId = selectedBranch.id;

        const paymentMethodButton = document.querySelector('.shipment__page--list--item.payment.active');
        if (!paymentMethodButton) {
            alert("Пожалуйста, выберите способ оплаты.");
            return;
        }
        const paymentMethodId = paymentMethodButton.dataset.id;

        const comment = document.querySelector('#text_comment').value.trim();

        if (!name) {
            alert("Пожалуйста, укажите ваше имя.");
            return;
        }

        if (!phone && !email) {
            alert("Пожалуйста, укажите хотя бы телефон или email для связи.");
            return;
        }

        // Собираем данные о товарах и их количестве
        const productsData = {};
        document.querySelectorAll('.product--amount__input').forEach(input => {
            const productId = input.closest('.cart__product--value').dataset.productId;
            const quantity = parseInt(input.value, 10);
            if (quantity > 0) {  // Добавляем только товары с количеством больше 0
                productsData[productId] = quantity;
            }
        });

        if (Object.keys(productsData).length === 0) {
            alert("Корзина пуста. Добавьте товары перед оформлением заказа.");
            return;
        }

        const goodsCost = window.currentTotalPrice || 0;
        const finalCost = window.applyDiscount ? window.applyDiscount() : goodsCost;

        // Получаем промокод из localStorage
        const appliedPromoCode = localStorage.getItem('appliedPromoCode') || null;
        console.log(`Промокод из localStorage: ${appliedPromoCode}`);

        const orderData = {
            name: name,
            phone: phone,
            email: email,
            shipment_method: shipmentMethodId,
            order_place: orderPlaceId,
            payment_method: paymentMethodId,
            comment: comment,
            goods_cost: finalCost,
            shipment_cost: shipmentCost,
            products: productsData,  // Отправляем {product_id: quantity}
            promo_code: appliedPromoCode,
        };

        try {
            const response = await fetch("/create-order/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify(orderData)
            });

            const data = await response.json();

            if (data.success) {
                alert("Ваш заказ принят");
                localStorage.removeItem('promoDiscount');
                localStorage.removeItem('appliedPromoCode');
                window.location.reload();
            } else {
                alert(`Ошибка: ${data.error}`);
            }
        } catch (error) {
            console.error("Ошибка при создании заказа:", error);
            alert("Произошла ошибка при создании заказа. Пожалуйста, попробуйте снова.");
        }
    });

    function getCsrfToken() {
        const name = 'csrftoken';
        const cookieValue = document.cookie.split('; ')
            .find(row => row.startsWith(name))
            ?.split('=')[1];
        return cookieValue || '';
    }
});