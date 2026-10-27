// Общая логика кнопки "Купить" (добавление в корзину) для всего сайта:
// карточки товара в каталоге/поиске/на главной, страница товара, избранное.
// Используется делегирование событий, поэтому карточки, подгруженные позже
// через AJAX-пагинацию, тоже работают без повторной инициализации.

function getCsrfToken() {
    const name = 'csrftoken';
    const cookieValue = document.cookie.split('; ')
        .find(row => row.startsWith(name))
        ?.split('=')[1];
    return cookieValue || '';
}

document.addEventListener('click', function (event) {
    const button = event.target.closest('.buy__btn');
    if (!button) return;

    event.preventDefault();

    const productId = button.dataset.productId;
    if (!productId) {
        // Кнопка без привязанного товара (например, в блоке "похожие товары"
        // на заглушках) — добавлять в корзину нечего.
        return;
    }

    if (button.dataset.pending === 'true') return;
    button.dataset.pending = 'true';

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(() => {
            alert(gettext('Товар добавлен в корзину!'));
        })
        .catch(error => {
            console.error('Ошибка добавления в корзину:', error);
            alert(gettext('Ошибка при добавлении товара.'));
        })
        .finally(() => {
            button.dataset.pending = 'false';
        });
});
