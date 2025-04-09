$(function() {
    // Глобальна змінна для зберігання параметрів фільтрів
    let filterParams = {};

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

                    // Більше не скидаємо data-current-page до 1
                    console.log('Updated pagination after filter update');
                } else {
                    $('#pagination-container').html('');
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error:', status, error);
            }
        });
    }

    // Обробка зміни фільтрів
    $('input[type="checkbox"]').on('change', function() {
        if ($(this).hasClass('binding-substance-checkbox')) {
            $('.binding-substance-checkbox').not(this).prop('checked', false);
        }
        updateProducts();
    });

    // Обробка кліку на кнопках сортування
    $('.sort-type').on('click', function() {
        // Знімаємо клас active з усіх кнопок
        $('.sort-type').removeClass('active');
        // Додаємо клас active до натиснутої кнопки
        $(this).addClass('active');
        // Оновлюємо товари з новим сортуванням
        updateProducts();
    });
});