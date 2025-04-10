$(function() {
    // Глобальна змінна для зберігання параметрів фільтрів
    let filterParams = {};

    // Змінні для зберігання глобальних меж
    let globalMinPrice = 0;
    let globalMaxPrice = 500;

    function updateProducts() {
        let url = '/catalogue/';
        let data = {
            page: 1,
            type: [],
            volume: [],
        };

        // Отримуємо тип сортування
        let sortType = $('.sort-type.active').attr('id')?.replace('sort_type_', '') || 'popularity';
        data.sort_type = sortType;

        // Отримуємо значення фільтрів
        let typeInputs = $('input[name="type"]:checked');
        console.log('Type inputs found:', typeInputs.length);
        typeInputs.each(function() {
            let value = $(this).val();
            console.log('Type value:', value);
            data.type.push(value);
        });

        let bindingSubstance = $('input[name="binding_substance"]:checked').val();
        console.log('Binding substance:', bindingSubstance);
        if (bindingSubstance) {
            data.binding_substance = bindingSubstance;
        }

        let volumeInputs = $('input[name="volume"]:checked');
        console.log('Volume inputs found:', volumeInputs.length);
        volumeInputs.each(function() {
            let value = $(this).val();
            console.log('Volume value:', value);
            data.volume.push(value);
        });

        data.is_discounted = $('input[name="is_discounted"]').is(':checked');
        data.is_new = $('input[name="is_new"]').is(':checked');
        data.is_in_stock = $('input[name="is_in_stock"]').is(':checked');

        // Додаємо параметри ціни з глобальної змінної filterParams, якщо вони є
        if (filterParams.price_gte !== undefined) {
            data.price_gte = filterParams.price_gte;
        }
        if (filterParams.price_lte !== undefined) {
            data.price_lte = filterParams.price_lte;
        }

        console.log('Final filter data:', data);

        // Зберігаємо параметри фільтрів у глобальну змінну
        filterParams = { ...data };
        delete filterParams.page;
        delete filterParams.load_more;
        console.log('Saved filter params:', filterParams);
        window.filterParams = filterParams;

        let queryString = $.param(data, true);
        console.log('Query string:', queryString);

        $.ajax({
            url: url,
            type: 'GET',
            data: queryString,
            success: function(response) {
                $('#products-container').html(response.new_items_html || response);
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

                    console.log('Updated pagination after filter update');
                } else {
                    $('#pagination-container').html('');
                }

                // Оновлюємо глобальні межі
                if (response.global_min_price !== undefined && response.global_max_price !== undefined) {
                    globalMinPrice = response.global_min_price;
                    globalMaxPrice = response.global_max_price;

                    // Оновлюємо межі в коді слайдерів
                    if (window.sliderUtils) {
                        window.sliderUtils.setGlobalMinPrice(globalMinPrice);
                        window.sliderUtils.setGlobalMaxPrice(globalMaxPrice);
                    }

                    // Оновлюємо атрибути min і max у слайдерів
                    $('#slider-low').attr('min', globalMinPrice).attr('max', globalMaxPrice);
                    $('#slider-high').attr('min', globalMinPrice).attr('max', globalMaxPrice);
                }

                // Оновлюємо поля введення на основі мінімальної і максимальної ціни
                if (response.min_price !== undefined && response.max_price !== undefined) {
                    $('#filter_price_gte').val(response.min_price);
                    $('#filter_price_lte').val(response.max_price);

                    // Оновлюємо слайдери
                    $('#slider-low').val(response.min_price);
                    $('#slider-high').val(response.max_price);

                    // Викликаємо updateFill для оновлення червоної лінії
                    if (window.sliderUtils) {
                        window.sliderUtils.updateFill();
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error:', status, error);
            }
        });
    }

    // Обробка зміни фільтрів (чекбокси)
    $('input[type="checkbox"]').on('change', function() {
        if ($(this).hasClass('binding-substance-checkbox')) {
            $('.binding-substance-checkbox').not(this).prop('checked', false);
        }
        updateProducts();
    });

    // Обробка кліку на кнопках сортування
    $('.sort-type').on('click', function() {
        $('.sort-type').removeClass('active');
        $(this).addClass('active');
        updateProducts();
    });

    // Обробка натискання кнопки "ОК" для фільтрації за ціною
    $('.price__filter--form').on('submit', function(e) {
        e.preventDefault(); // Запобігаємо стандартному відправленню форми

        // Отримуємо значення з полів введення
        let priceGte = parseInt($('#filter_price_gte').val()) || globalMinPrice;
        let priceLte = parseInt($('#filter_price_lte').val()) || globalMaxPrice;

        // Перевірка меж на основі globalMinPrice і globalMaxPrice
        if (priceGte < globalMinPrice) {
            priceGte = globalMinPrice;
            $('#filter_price_gte').val(priceGte);
        }
        if (priceLte > globalMaxPrice) {
            priceLte = globalMaxPrice;
            $('#filter_price_lte').val(priceLte);
        }
        if (priceGte > priceLte) {
            priceGte = priceLte;
            $('#filter_price_gte').val(priceGte);
        }

        // Оновлюємо глобальні параметри фільтрів
        filterParams.price_gte = priceGte;
        filterParams.price_lte = priceLte;

        // Оновлюємо товари
        updateProducts();
    });

    // Ініціалізація: Викликаємо updateProducts при завантаженні сторінки
    updateProducts();
});