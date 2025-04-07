document.addEventListener("DOMContentLoaded", async function () {
    let discount = null;
    let appliedPromoCode = null;

    window.applyDiscount = function applyDiscount() {
        const totalPrice = window.currentTotalPrice || 0;
        let discountedPrice = totalPrice;
        if (discount) {
            if (discount.type === 'amount') {
                discountedPrice = totalPrice - discount.value;
            } else if (discount.type === 'percent') {
                discountedPrice = totalPrice * (1 - discount.value / 100);
            }
            discountedPrice = Math.max(0, discountedPrice);
        }
        const discountedPriceElement = document.querySelector('#total-price-with-discount');
        if (discountedPriceElement) {
            discountedPriceElement.textContent = discountedPrice.toFixed(2).replace('.', ',') + '₴';
        }
        return discountedPrice;
    };

    const savedDiscount = localStorage.getItem('promoDiscount');
    const savedPromoCode = localStorage.getItem('appliedPromoCode');
    if (savedDiscount && savedPromoCode) {
        discount = JSON.parse(savedDiscount);
        appliedPromoCode = savedPromoCode;
        document.querySelector('.checkout__discount--code__input--field').value = savedPromoCode;
        document.querySelector('.checkout__discount--code__input--field').disabled = true;
        document.querySelector('.checkout__discount--code__btn').disabled = true;
        await window.updateTotalPrice();
        applyDiscount();
    }

    document.querySelector(".checkout__discount--code__btn").addEventListener("click", async function (e) {
        e.preventDefault();

        let promoInput = document.querySelector(".checkout__discount--code__input--field");
        let promoCode = promoInput.value.trim();

        if (!promoCode) {
            alert("Введите промокод.");
            return;
        }

        if (appliedPromoCode === promoCode) {
            alert("Этот промокод уже применен.");
            return;
        }

        let formData = new FormData();
        formData.append("code", promoCode);

        try {
            const response = await fetch("/apply-promo/", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                },
            });

            const data = await response.json();

            if (data.success) {
                const discountValue = parseFloat(data.discount);
                discount = {
                    type: data.discount.includes('%') ? 'percent' : 'amount',
                    value: discountValue
                };
                appliedPromoCode = promoCode;

                localStorage.setItem('promoDiscount', JSON.stringify(discount));
                localStorage.setItem('appliedPromoCode', promoCode);
                console.log(`Сохранен промокод в localStorage: ${promoCode}`);

                promoInput.disabled = true;
                document.querySelector('.checkout__discount--code__btn').disabled = true;

                alert(`Промокод применен! Ваша скидка: ${data.discount}`);
                await window.updateTotalPrice();
                applyDiscount();
            } else {
                alert(`Ошибка: ${data.error}`);
            }
        } catch (error) {
            console.error("Ошибка запроса:", error);
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