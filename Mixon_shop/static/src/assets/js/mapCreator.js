function initMap() {}

function setupMapListeners() {
    const mapRegular = document.querySelector("#map-regular");
    const markerRegular = document.querySelector("#marker-regular");
    const mapModal = document.querySelector("#map-modal");
    const markerModal = document.querySelector("#marker-modal");
    const branches = document.querySelectorAll(".widget__form--check__list");
    const mapButtons = document.querySelectorAll(".show--map--btn");
    const mapModalWindow = document.querySelector("#mapModal");
    const closeModal = document.querySelector(".map-modal-close");
    const isContactsPage = document.querySelector(".addresses--block") !== null;

    function updateMap(mapInfo) {

        // Извлекаем координаты из mapInfo
        const lat = parseFloat(mapInfo.split(",")[0].split(":")[1]);
        const lng = parseFloat(mapInfo.split(",")[1].split(":")[1]);

        if (window.innerWidth < 768 && !isContactsPage) {
            // На маленьких экранах (не Contacts) используем фиксированные координаты для модальной карты
            if (mapModal && markerModal) {
                mapModal.setAttribute("center", `${lat},${lng}`);
                markerModal.setAttribute("position", `${lat},${lng}`);
                mapModal.setAttribute("zoom", "15");
            }
        } else {
            // На больших экранах или странице Contacts используем mapInfo для обычной карты
            if (mapRegular && markerRegular) {
                mapRegular.setAttribute("center", `${lat},${lng}`);
                markerRegular.setAttribute("position", `${lat},${lng}`);
                mapRegular.setAttribute("zoom", "15");
            }
        }
    }

    // Обработчик для кнопок "Показать на карте"
    mapButtons.forEach(button => {
        button.addEventListener("click", function (e) {
            e.stopPropagation();
            const mapInfo = this.getAttribute("data-map-info");
            updateMap(mapInfo);
            // Открываем модальное окно только на маленьких экранах и не на странице Contacts
            if (window.innerWidth < 768 && !isContactsPage && mapModalWindow) {
                mapModalWindow.classList.add("active");
            }
        });
    });

    // Обработчик для закрытия модального окна
    if (closeModal) {
        closeModal.addEventListener("click", function () {
            mapModalWindow.classList.remove("active");
        });
    }

    // Закрытие модального окна при клике вне карты
    if (mapModalWindow) {
        mapModalWindow.addEventListener("click", function (e) {
            if (e.target === mapModalWindow) {
                mapModalWindow.classList.remove("active");
            }
        });
    }

    // Закрытие по клавише Esc
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && mapModalWindow && mapModalWindow.classList.contains("active")) {
            mapModalWindow.classList.remove("active");
        }
    });

    // Обработчик для элементов списка
    branches.forEach(branch => {
        branch.addEventListener("click", function (e) {
            if (!e.target.classList.contains("show--map--btn")) {
                const mapInfo = this.getAttribute("data-map-info");
                // Обновляем карту только на больших экранах или на странице Contacts
                if (window.innerWidth >= 768 || isContactsPage) {
                    updateMap(mapInfo);
                }
            }
        });
    });

    // Обновление при изменении размера окна
    window.addEventListener("resize", function () {
        if (window.innerWidth >= 768 && mapModalWindow && mapModalWindow.classList.contains("active")) {
            mapModalWindow.classList.remove("active"); // Закрываем модальное окно на больших экранах
        }
    });
}

// Делаем setupMapListeners доступной глобально
window.setupMapListeners = setupMapListeners;

// Вызываем при загрузке страницы, если элементы уже есть
document.addEventListener("DOMContentLoaded", function () {
    if (document.querySelector(".widget__form--check__list")) {
        setupMapListeners();
    }
});