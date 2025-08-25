$(function () {
    let filterParams = {};

    let globalMinPrice = 0;
    let globalMaxPrice = 500;

    function updateProducts(page = 1) {
        let url = '/catalogue/';
        let data = {
            page: page,
            type: [],
            volume: [],
        };

        let sortType = $('.sort-type.active').attr('id')?.replace('sort_type_', '') || 'popularity';
        data.sort_type = sortType;

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

        // Добавляем product_category_id из URL
        let params = new URLSearchParams(window.location.search);
        let productCategoryId = params.get('product_category_id');
        if (productCategoryId) {
            data.product_category_id = productCategoryId;
        }

        if (filterParams.price_gte !== undefined) {
            data.price_gte = filterParams.price_gte;
        }
        if (filterParams.price_lte !== undefined) {
            data.price_lte = filterParams.price_lte;
        }

        console.log('Final filter data:', data);

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
            traditional: true,
            success: function(response) {
                $('#products-container').html(response.new_items_html || response);
                if (response.new_pagination_html) {
                    let $newPagination = $(response.new_pagination_html);
                    let $newPaginationContainer = $newPagination.find('#pagination-container').html() || '';
                    $('#pagination-container').html($newPaginationContainer);

                    let $newLoadMoreContainer = $newPagination.find('#load-more-container').html() || '';
                    if ($newLoadMoreContainer.trim()) {
                        $('#load-more-container').html($newLoadMoreContainer);
                    } else {
                        $('#load-more-container').html('');
                    }
                    console.log('Updated pagination after filter update');
                } else {
                    $('#pagination-container').html('');
                }

                if (response.global_min_price !== undefined && response.global_max_price !== undefined) {
                    globalMinPrice = response.global_min_price;
                    globalMaxPrice = response.global_max_price;

                    if (window.sliderUtils) {
                        window.sliderUtils.setGlobalMinPrice(globalMinPrice);
                        window.sliderUtils.setGlobalMaxPrice(globalMaxPrice);
                    }

                    $('#slider-low').attr('min', globalMinPrice).attr('max', globalMaxPrice);
                    $('#slider-high').attr('min', globalMinPrice).attr('max', globalMaxPrice);
                }

                if (response.min_price !== undefined && response.max_price !== undefined) {
                    $('#filter_price_gte').val(response.min_price);
                    $('#filter_price_lte').val(response.max_price);

                    $('#slider-low').val(response.min_price);
                    $('#slider-high').val(response.max_price);

                    if (window.sliderUtils) {
                        window.sliderUtils.updateFill();
                    }
                }

                if (window.updatePageState) {
                    window.updatePageState(1);
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error:', status, error);
            }
        });
    }

    $('input[type="checkbox"]').on('change', function() {
        if ($(this).hasClass('binding-substance-checkbox')) {
            $('.binding-substance-checkbox').not(this).prop('checked', false);
        }
        updateProducts(1);
    });

    $('.sort-type').on('click', function() {
        $('.sort-type').removeClass('active');
        $(this).addClass('active');
        updateProducts(1);
    });

    $('.price__filter--form').on('submit', function(e) {
        e.preventDefault();

        let priceGte = parseInt($('#filter_price_gte').val()) || globalMinPrice;
        let priceLte = parseInt($('#filter_price_lte').val()) || globalMaxPrice;

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

        filterParams.price_gte = priceGte;
        filterParams.price_lte = priceLte;

        updateProducts(1);
    });

    $(document).ready(function() {
        let params = new URLSearchParams(window.location.search);
        let page = params.get('page') || '1';
        updateProducts(parseInt(page));
    });
});