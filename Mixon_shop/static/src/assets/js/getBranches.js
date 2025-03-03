$(document).ready(function() {
    function loadBranches(cityId) {
        $.ajax({
            url: "/get-branches/",  // URL на представление Django
            type: "GET",
            data: { city_id: cityId },
            success: function(response) {
                $(".widget__form--check.only-one").html(response.html);  // Обновляем список филиалов
            },
            error: function(xhr, status, error) {
                console.error("Ошибка AJAX запроса:", error);
            }
        });
    }

    // Загружаем филиалы при загрузке страницы
    var initialCityId = $("#input_city").val();
    if (initialCityId) {
        loadBranches(initialCityId);
    }

    // Обрабатываем выбор города
    $("#input_city").change(function() {
        var cityId = $(this).val();
        loadBranches(cityId);
    });
});
