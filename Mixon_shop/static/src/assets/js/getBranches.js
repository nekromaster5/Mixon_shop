$(document).ready(function() {
    function loadBranches(cityId) {
        $.ajax({
            url: "/get-branches/",
            type: "GET",
            data: { city_id: cityId },
            success: function(response) {
                $(".widget__form--check.only-one").html(response.html);
                initializeExclusiveCheckboxes();
                // Вызываем setupMapListeners после загрузки новых филиалов
                if (typeof window.setupMapListeners === "function") {
                    window.setupMapListeners();
                    // Выбираем первый филиал и выделяем его
                    const firstBranch = document.querySelector(".widget__form--check__list");
                    if (firstBranch) {
                        // Находим чекбокс внутри первого филиала
                        const firstCheckbox = firstBranch.querySelector("input[type='checkbox']");
                        if (firstCheckbox) {
                            firstCheckbox.checked = true; // Выделяем чекбокс
                        }
                        // Сразу обновляем карту, вызвав клик на первом филиале
                        firstBranch.click();
                    }
                } else {
                    console.error("setupMapListeners is not defined!");
                }
            },
            error: function(xhr, status, error) {
                console.error("Ошибка AJAX запроса:", error);
            }
        });
    }

    var initialCityId = $("#input_city").val();
    if (initialCityId) {
        loadBranches(initialCityId);
    }

    $("#input_city").change(function() {
        var cityId = $(this).val();
        loadBranches(cityId);
    });
});