$(document).ready(function () {
    var currentPage = parseInt($('#load-more').data('current-page'));
    var totalPages = parseInt($('#load-more').data('total-pages'));
    var query = $('#load-more').data('query');

    $('#load-more').on('click', function () {
        if (currentPage < totalPages) {
            currentPage++;
            var url = $(this).data('url') + '?page=' + currentPage;
            if (query) {
                url += '&query=' + query;
            }

            $.ajax({
                url: url,
                success: function (data) {
                    $('#products-container').append(data.html);
                    if (currentPage >= totalPages) {
                        $('#load-more').hide();
                    }
                    // Update the data attribute for the current page
                    $('#load-more').data('current-page', currentPage);
                }
            });
        }
    });
});
