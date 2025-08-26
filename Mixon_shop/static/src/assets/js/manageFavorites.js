function initWishlistButtons(context = document) {
    context.querySelectorAll('.product__card--action__btn.wishlist').forEach(btn => {
        if (!btn.dataset.bound) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();

                const productId = this.dataset.productId;
                if (!productId) return;

                // Отправляем AJAX-запрос
                fetch(this.href, {
                    method: 'GET',
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                .then(res => {
                    if (res.status === 403) {
                        alert('Please log in to manage your wishlist.');
                        return null;
                    }
                    if (!res.ok) throw new Error('Network response was not ok');
                    return res.json();
                })
                .then(data => {
                    if (!data) return;

                    // Находим все кнопки с тем же product_id
                    const allButtons = document.querySelectorAll(`.product__card--action__btn.wishlist[data-product-id="${productId}"]`);
                    const isFavorite = data.status === 'added';

                    // Обновляем состояние всех кнопок
                    allButtons.forEach(button => {
                        const svgPath = button.querySelector('svg path');
                        if (isFavorite) {
                            svgPath.setAttribute('fill', 'red');
                            button.dataset.isFavorite = 'true';
                        } else {
                            svgPath.removeAttribute('fill');
                            button.dataset.isFavorite = 'false';
                        }
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Нужно быть зарегистрированным пользователем, чтобы добавлять в закладки');
                });
            });
            btn.dataset.bound = 'true';
        }
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    initWishlistButtons();
});

// Функция для обновления кнопок при динамической подгрузке
function updateWishlistButtons(context = document) {
    initWishlistButtons(context);
}