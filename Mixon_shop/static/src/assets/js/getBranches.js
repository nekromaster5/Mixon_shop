$(document).ready(function() {
    function loadBranches(cityId, templateName) {
        $.ajax({
            url: "/get-branches/",
            type: "GET",
            data: {
                city_id: cityId,
                template: templateName
            },
            success: function(response) {
                $(".widget__form--check.only-one").html(response.html);
                initializeExclusiveCheckboxes(templateName);
                // Вызываем setupMapListeners после загрузки новых филиалов
                if (typeof window.setupMapListeners === "function") {
                    window.setupMapListeners();
                    // Выбираем первый филиал и выделяем его
                    const firstBranch = document.querySelector(".widget__form--check__list");
                    if (firstBranch) {
                        const firstCheckbox = firstBranch.querySelector("input[type='checkbox']");
                        const firstLabel = firstBranch.querySelector(".shop_address");
                        if (firstCheckbox) {
                            firstCheckbox.checked = true; // Выделяем чекбокс
                            if (templateName === 'contacts' && firstLabel) {
                                firstLabel.classList.add("active"); // Добавляем класс active только для contacts
                            }
                            // Обновляем информацию о филиале только для contacts
                            if (templateName === 'contacts') {
                                updateBranchInfo(firstBranch);
                            }
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

    // Функция для обновления информации о филиале (только для contacts)
    function updateBranchInfo(branchElement) {
        const branchId = branchElement.querySelector("input[type='checkbox']").id;
        $.ajax({
            url: "/get-branch-details/",
            type: "GET",
            data: { branch_id: branchId },
            success: function(response) {
                // Обновляем информацию о филиале
                const branchInfoContainer = document.querySelector(".branch-info");
                if (branchInfoContainer) {
                    branchInfoContainer.innerHTML = response.html;
                }
            },
            error: function(xhr, status, error) {
                console.error("Ошибка при загрузке данных филиала:", error);
            }
        });
    }

    // Обеспечиваем эксклюзивность чекбоксов с учетом страницы
    function initializeExclusiveCheckboxes(templateName) {
        $(".widget__form--check__list").on("click", function() {
            const checkbox = $(this).find("input[type='checkbox']");
            const label = $(this).find(".shop_address");

            // Снимаем выделение со всех чекбоксов
            $(".widget__form--check__input").prop("checked", false);
            // Удаляем класс active у всех label (только для contacts)
            if (templateName === 'contacts') {
                $(".shop_address").removeClass("active");
            }

            // Устанавливаем текущий чекбокс
            checkbox.prop("checked", true);
            // Добавляем класс active только для contacts
            if (templateName === 'contacts' && label.length) {
                label.addClass("active");
            }

            // Обновляем информацию о филиале только для contacts
            if (templateName === 'contacts') {
                updateBranchInfo(this);
            }
        });
    }

    // Определяем, с какой страницы вызывается скрипт
    var templateName = window.location.pathname.includes('contacts') ? 'contacts' : 'checkout';

    // Проверяем начальные значения для input_city и input_city2
    var initialCityId = $("#input_city").val() || $("#input_city2").val();
    if (initialCityId) {
        loadBranches(initialCityId, templateName);
    }

    // Отслеживаем изменения в input_city
    $("#input_city").change(function() {
        var cityId = $(this).val();
        if (cityId) {
            loadBranches(cityId, templateName);
        }
    });

    // Отслеживаем изменения в input_city2
    $("#input_city2").change(function() {
        var cityId = $(this).val();
        if (cityId) {
            loadBranches(cityId, templateName);
        }
    });
});