$(function() {
    // Зберігаємо початковий HTML кнопки "Показать ще" для відновлення
    let initialLoadMoreHtml = $('#load-more-container').html();

    // Зберігаємо початкові значення url, query і pageType
    let globalUrl = $('#load-more-btn').data('url') || '/search/';
    let globalQuery = decodeURIComponent($('#load-more-btn').data('query') || '');
    let globalPageType = $('#load-more-btn').data('page-type') || 'search';

    console.log('Initial globalUrl (search):', globalUrl);
    console.log('Initial globalQuery (search):', globalQuery);
    console.log('Initial globalPageType (search):', globalPageType);

    // Обробка "Показать ще"
    $(document).on('click', '#load-more-btn', function(e) {
        e.preventDefault();
        let $btn = $(this);
        let currentPage = parseInt($btn.data('current-page'));
        let url = $btn.data('url') || globalUrl;
        let query = decodeURIComponent($btn.data('query') || globalQuery);
        let productType = $btn.data('product-type') || '';
        let pageType = $btn.data('page-type') || globalPageType;

        let data = {
            page: currentPage,
            load_more: 1,
            query: query,
            page_type: pageType
        };

        console.log('window.filterParams before merge (search):', window.filterParams);
        if (window.filterParams) {
            Object.assign(data, window.filterParams);
        }
        console.log('Data after merge (search):', data);
        console.log('URL for load more (search):', url);

        let queryString = $.param(data, true);
        console.log('Query string for load more (search):', queryString);

        let nextPage = currentPage + 1;

        $.ajax({
            url: url,
            type: 'GET',
            data: queryString,
            success: function(response) {
                console.log('Response (search):', response);
                $('#products-container').append(response.new_items_html);
                if (!response.new_items_html.trim()) {
                    $('#load-more-container').html(''); // Прибираємо кнопку, якщо більше немає сторінок
                }
                if (response.new_pagination_html) {
                    // Оновлюємо #pagination-container
                    let $newPagination = $(response.new_pagination_html);
                    let $newPaginationContainer = $newPagination.find('#pagination-container').html() || '';
                    $('#pagination-container').html($newPaginationContainer);

                    // Перевіряємо, чи є наступна сторінка, і відновлюємо кнопку, якщо потрібно
                    let $newLoadMoreContainer = $newPagination.find('#load-more-container').html() || '';
                    if ($newLoadMoreContainer.trim()) {
                        $('#load-more-container').html($newLoadMoreContainer);
                    }

                    // Оновлюємо data-current-page у кнопці
                    $('#load-more-btn').data('current-page', nextPage);
                    console.log('Updated data-current-page to (search):', nextPage);
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error (search):', status, error);
            }
        });
    });

    // Обробка стрілок і номерів сторінок
    $(document).on('click', '.ajax-page-link', function(e) {
        e.preventDefault();
        let $btn = $(this);
        let page = parseInt($btn.data('page'));
        let url = $btn.closest('.pagination__area').find('#load-more-btn').data('url') || globalUrl;
        let query = decodeURIComponent($btn.closest('.pagination__area').find('#load-more-btn').data('query') || globalQuery);
        let productType = $btn.closest('.pagination__area').find('#load-more-btn').data('product-type') || '';
        let pageType = $btn.closest('.pagination__area').find('#load-more-btn').data('page-type') || globalPageType;

        let data = {
            page: page,
            query: query,
            page_type: pageType
        };

        console.log('window.filterParams before merge (ajax-page-link, search):', window.filterParams);
        if (window.filterParams) {
            Object.assign(data, window.filterParams);
        }
        console.log('Data after merge (ajax-page-link, search):', data);
        console.log('URL for ajax-page-link (search):', url);

        let queryString = $.param(data, true);
        console.log('Query string for ajax-page-link (search):', queryString);

        $.ajax({
            url: url,
            type: 'GET',
            data: queryString,
            success: function(response) {
                console.log('Response (ajax-page-link, search):', response);
                $('#products-container').html(response.new_items_html);
                if (response.new_pagination_html) {
                    // Оновлюємо #pagination-container
                    let $newPagination = $(response.new_pagination_html);
                    let $newPaginationContainer = $newPagination.find('#pagination-container').html() || '';
                    $('#pagination-container').html($newPaginationContainer);

                    // Перевіряємо, чи є наступна сторінка, і відновлюємо кнопку, якщо потрібно
                    let $newLoadMoreContainer = $newPagination.find('#load-more-container').html() || '';
                    if ($newLoadMoreContainer.trim()) {
                        $('#load-more-container').html($newLoadMoreContainer);
                    }

                    // Оновлюємо data-current-page у кнопці
                    $('#load-more-btn').data('current-page', page);
                    console.log('Updated data-current-page to (ajax-page-link, search):', page);
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error (ajax-page-link, search):', status, error);
            }
        });
    });
});