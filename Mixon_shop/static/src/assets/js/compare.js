function getCookie(name) {
    const match = document.cookie.split('; ').find(row => row.startsWith(name + '='));
    return match ? decodeURIComponent(match.split('=')[1]) : '';
}

function updateCompareCounter(count) {
    document.querySelectorAll('[data-compare-count]').forEach(badge => {
        badge.textContent = count;
        badge.hidden = count === 0;
    });
}

document.addEventListener('click', function (e) {
    const btn = e.target.closest('.compare-button');
    if (!btn) return;
    e.preventDefault();

    fetch(btn.href, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
        .then(res => {
            if (!res.ok) throw new Error('Network response was not ok');
            return res.json();
        })
        .then(data => {
            if (data.status === 'full') {
                alert(data.message);
                return;
            }
            const productId = btn.dataset.productId;
            document.querySelectorAll(`.compare-button[data-product-id="${productId}"]`).forEach(button => {
                button.classList.toggle('is-active', data.status === 'added');
            });
            updateCompareCounter(data.count);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Не удалось обновить сравнение. Попробуйте ещё раз.');
        });
});
