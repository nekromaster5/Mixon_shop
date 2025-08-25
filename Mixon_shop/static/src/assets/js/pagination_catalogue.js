$(function () {
    let loadedPages = parseInt($('#load-more-btn').data('current-page')) || 1;

    window.updatePageState = function(newPage) {
        loadedPages = newPage;
        $('#load-more-btn').data('current-page', loadedPages);
        updateUrl();
    };

    function getUrlParams() {
        let params = new URLSearchParams(window.location.search);
        let result = {};
        for (let [key, value] of params) {
            if (value && !/^\s+$/.test(value)) {
                if (result[key]) {
                    if (Array.isArray(result[key])) {
                        result[key].push(value);
                    } else {
                        result[key] = [result[key], value];
                    }
                } else {
                    result[key] = value;
                }
            }
        }
        return result;
    }

    function initializeState() {
        let params = getUrlParams();
        if (params.page) {
            loadedPages = parseInt(params.page) || 1;
            $('#load-more-btn').data('current-page', loadedPages);
        }
        window.filterParams = window.filterParams || {};
        Object.assign(window.filterParams, params); // Сохраняем product_category_id
        if (typeof updateProducts === 'function') {
            updateProducts(loadedPages);
        }
    }

    function updateUrl() {
        let sortType = $('.sort-type.active').attr('id')?.replace('sort_type_', '') || 'popularity';
        let filterParams = window.filterParams || {};
        let query = $('#load-more-btn').data('query') || '';
        let productCategoryId = filterParams.product_category_id || ''; // Получаем из filterParams

        let data = {
            page: loadedPages,
            type: filterParams.type || [],
            binding_substance: filterParams.binding_substance || '',
            volume: filterParams.volume || [],
            is_discounted: filterParams.is_discounted || false,
            is_new: filterParams.is_new || false,
            is_in_stock: filterParams.is_in_stock || false,
            sort_type: sortType !== 'popularity' ? sortType : undefined,
            price_gte: filterParams.price_gte || '',
            price_lte: filterParams.price_lte || ''
        };

        if (query) {
            data.query = query;
        }
        if (productCategoryId) {
            data.product_category_id = productCategoryId; // Добавляем category
        }

        let filteredData = Object.fromEntries(
            Object.entries(data).filter(([key, value]) => {
                if (Array.isArray(value)) return value.length > 0;
                if (value === '' || value === false || value === undefined) return false;
                if (key === 'sort_type' && value === 'popularity') return false;
                return true;
            })
        );

        let queryString = $.param(filteredData, true);
        let newUrl = $('#load-more-btn').data('url') || window.location.pathname;
        newUrl = queryString ? `${newUrl}?${queryString}` : newUrl;

        history.pushState({ page: loadedPages, filters: filteredData }, '', newUrl);
        console.log('Updated URL:', newUrl);
    }

    $(document).on('click', '#load-more-btn', function (e) {
        e.preventDefault();

        let nextPage = loadedPages + 1;
        let url = $(this).data('url');
        let query = $(this).data('query') || '';
        let productCategoryId = window.filterParams.product_category_id || '';
        let pageType = $(this).data('page-type');

        let sortType = $('.sort-type.active').attr('id')?.replace('sort_type_', '') || 'popularity';
        let filterParams = window.filterParams || {};

        let data = {
            page: nextPage,
            load_more: true,
            type: filterParams.type || [],
            binding_substance: filterParams.binding_substance || '',
            volume: filterParams.volume || [],
            is_discounted: filterParams.is_discounted || false,
            is_new: filterParams.is_new || false,
            is_in_stock: filterParams.is_in_stock || false,
            sort_type: sortType,
            price_gte: filterParams.price_gte || '',
            price_lte: filterParams.price_lte || ''
        };

        if (query) {
            data.query = query;
        }
        if (productCategoryId) {
            data.product_category_id = productCategoryId;
        }

        console.log('Load more data:', data);

        $.ajax({
            url: url,
            type: 'GET',
            data: data,
            traditional: true,
            success: function (response) {
                console.log('Response (load-more, ' + pageType + '):', response);
                $('#products-container').append(response.new_items_html);

                let $newPagination = $(response.new_pagination_html);
                let $newPaginationContainer = $newPagination.find('#pagination-container').html() || '';
                $('#pagination-container').html($newPaginationContainer);

                let $newLoadMoreContainer = $newPagination.find('#load-more-container').html() || '';
                if ($newLoadMoreContainer.trim()) {
                    $('#load-more-container').html($newLoadMoreContainer);
                    loadedPages = nextPage;
                    $('#load-more-btn').data('current-page', loadedPages);
                } else {
                    loadedPages = nextPage;
                    $('#load-more-btn').data('current-page', loadedPages);
                    $('#load-more-container').html('');
                }

                updateUrl();
            },
            error: function (xhr, status, error) {
                console.error('AJAX error:', status, error);
            }
        });
    });

    $(document).on('click', '.ajax-page-link', function (e) {
        e.preventDefault();

        let page = $(this).data('page');
        let url = $(this).attr('href').split('?')[0];
        let query = $('#load-more-btn').data('query') || '';
        let productCategoryId = window.filterParams.product_category_id || '';
        let pageType = $('#load-more-btn').data('page-type');

        let sortType = $('.sort-type.active').attr('id')?.replace('sort_type_', '') || 'popularity';
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
            price_gte: filterParams.price_gte || '',
            price_lte: filterParams.price_lte || ''
        };

        if (query) {
            data.query = query;
        }
        if (productCategoryId) {
            data.product_category_id = productCategoryId;
        }

        console.log('Page link data:', data);

        $.ajax({
            url: url,
            type: 'GET',
            data: data,
            traditional: true,
            success: function (response) {
                console.log('Response (ajax-page-link, ' + pageType + '):', response);
                $('#products-container').html(response.new_items_html);

                let $newPagination = $(response.new_pagination_html);
                let $newPaginationContainer = $newPagination.find('#pagination-container').html() || '';
                $('#pagination-container').html($newPaginationContainer);

                let $newLoadMoreContainer = $newPagination.find('#load-more-container').html() || '';
                if ($newLoadMoreContainer.trim()) {
                    $('#load-more-container').html($newLoadMoreContainer);
                } else {
                    $('#load-more-container').html('');
                }

                loadedPages = page;
                $('#load-more-btn').data('current-page', loadedPages);
                updateUrl();
            },
            error: function (xhr, status, error) {
                console.error('AJAX error:', status, error);
            }
        });
    });

    $(document).on('change', 'input[type="checkbox"]', function () {
        updateUrl();
    });

    $(document).on('click', '.sort-type', function () {
        updateUrl();
    });

    initializeState();

    window.onpopstate = function (event) {
        if (event.state) {
            loadedPages = event.state.page || 1;
            let filterParams = event.state.filters || {};
            window.filterParams = filterParams;
            if (typeof updateProducts === 'function') {
                updateProducts(loadedPages);
            }
        }
    };
});