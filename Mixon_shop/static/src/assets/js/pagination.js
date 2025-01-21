$(function() {
  $('#load-more-btn').on('click', function() {
    let $btn = $(this);
    let currentPage = parseInt($btn.data('current-page'));
    let query = $btn.data('query');
    let url = $btn.data('url');

    let nextPage = currentPage + 1;

    $.ajax({
      url: url,
      type: 'GET',
      data: {
        page: currentPage,   // «офіційно» зараз на currentPage
        load_more: 1,        // сигнал для view, що це «показати ще»
        query: query
      },
      success: function(response) {
        // Додаємо новий html у контейнер товарів
        $('#products-container').append(response.new_items_html);

        // Якщо прийшла порожня відповідач, отже більше сторінок нема
        if (!response.new_items_html.trim()) {
          $btn.hide();  // ховаємо кнопку
        }

        // Оновлюємо пагінацію
        if (response.new_pagination_html) {
          $('#pagination-container').html(response.new_pagination_html);
        }

        // Зсув «віртуальної» поточної сторінки (тепер уже на nextPage)
        $btn.data('current-page', nextPage);
      }
    });
  });
});