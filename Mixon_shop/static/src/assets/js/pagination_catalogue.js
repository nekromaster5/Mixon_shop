$(function() {
    // Глобальна змінна для відстеження кількості завантажених сторінок
    let loadedPages = 1;

    $(document).on('click', '#load-more-btn', function(e) {
        e.preventDefault();

        let currentPage = loadedPages;  // Використовуємо глобальну змінну
        let url = $(this).data('url');
        let query = $(this).data('query') || '';
        let productType = $(this).data('product-type') || '';
        let pageType = $(this).data('page-type');

        // Отримуємо тип сортування
        let sortType = $('.sort-type.active').attr('id')?.replace('sort_type_', '') || 'popularity';

        // Отримуємо параметри фільтрів із глобальної змінної
        let filterParams = window.filterParams || {};

        let data = {
            page: currentPage + 1,
            load_more: true,
            type: filterParams.type || [],
            binding_substance: filterParams.binding_substance || '',
            volume: filterParams.volume || [],
            is_discounted: filterParams.is_discounted || false,
            is_new: filterParams.is_new || false,
            is_in_stock: filterParams.is_in_stock || false,
            sort_type: sortType,
        };

        if (query) {
            data.query = query;
        }
        if (productType) {
            data.product_type = productType;
        }

        console.log('Load more data:', data);

        $.ajax({
            url: url,
            type: 'GET',
            data: data,
            success: function(response) {
                console.log('Response (ajax-page-link, ' + pageType + '):', response);
                $('#products-container').append(response.new_items_html);

                // Оновлюємо пагінацію, але враховуємо, що ми щойно додали сторінку
                let $newPagination = $(response.new_pagination_html);
                let $newPaginationContainer = $newPagination.find('#pagination-container').html() || '';
                $('#pagination-container').html($newPaginationContainer);

                let $newLoadMoreContainer = $newPagination.find('#load-more-container').html() || '';
                if ($newLoadMoreContainer.trim()) {
                    $('#load-more-container').html($newLoadMoreContainer);
                    loadedPages = currentPage + 1;  // Оновлюємо кількість завантажених сторінок
                    $('#load-more-btn').data('current-page', loadedPages);
                } else {
                    $('#load-more-container').html('');
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error:', status, error);
            }
        });
    });

    $(document).on('click', '.ajax-page-link', function(e) {
        e.preventDefault();

        let page = $(this).data('page');
        let url = $(this).attr('href').split('?')[0];
        let query = $('#load-more-btn').data('query') || '';
        let productType = $('#load-more-btn').data('product-type') || '';
        let pageType = $('#load-more-btn').data('page-type');

        // Отримуємо тип сортування
        let sortType = $('.sort-type.active').attr('id')?.replace('sort_type_', '') || 'popularity';

        // Отримуємо параметри фільтрів із глобальної змінної
        let filterParams = window.filterParams || {};

        let data = {
            page: page,
            type: filterParams.type || [],
            binding_substance: filterParams.binding_substance || '',
            volume: filterParams.volume || [],
            is_discounted: filterParams.is_discounted || false,
            is_new: filterParams.is_new || false,
            is_in_stock: filterParams.is_in_stock || false,
            sort_type: sortType,
        };

        if (query) {
            data.query = query;
        }
        if (productType) {
            data.product_type = productType;
        }

        console.log('Page link data:', data);

        $.ajax({
            url: url,
            type: 'GET',
            data: data,
            success: function(response) {
                console.log('Response (ajax-page-link, ' + pageType + '):', response);
                $('#products-container').html(response.new_items_html);

                let $newPagination = $(response.new_pagination_html);
                let $newPaginationContainer = $newPagination.find('#pagination-container').html() || '';
                $('#pagination-container').html($newPaginationContainer);

                let $newLoadMoreContainer = $newPagination.find('#load-more-container').html() || '';
                if ($newLoadMoreContainer.trim()) {
                    $('#load-more-container').html($newLoadMoreContainer);
                    loadedPages = page;  // Оновлюємо кількість завантажених сторінок
                    $('#load-more-btn').data('current-page', loadedPages);
                } else {
                    $('#load-more-container').html('');
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error:', status, error);
            }
        });
    });

    // Скидаємо loadedPages при зміні фільтрів або сортування
    $(document).on('change', 'input[type="checkbox"]', function() {
        loadedPages = 1;  // Скидаємо до 1 при зміні фільтрів
    });

    $(document).on('click', '.sort-type', function() {
        loadedPages = 1;  // Скидаємо до 1 при зміні сортування
    });
});