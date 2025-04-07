// mapCreator.js
function initMap() {}

function setupMapListeners() {
    const map = document.querySelector("gmp-map");
    const marker = document.querySelector("gmp-advanced-marker");

    const branches = document.querySelectorAll(".widget__form--check__list");
    const mapButtons = document.querySelectorAll(".show--map--btn");

    function updateMap(mapInfo) {
        const lat = parseFloat(mapInfo.split(",")[0].split(":")[1]);
        const lng = parseFloat(mapInfo.split(",")[1].split(":")[1]);
        map.setAttribute("center", `${lat},${lng}`);
        marker.setAttribute("position", `${lat},${lng}`);
        map.setAttribute("zoom", "15");
    }

    mapButtons.forEach(button => {
        button.addEventListener("click", function (e) {
            e.stopPropagation();
            const mapInfo = this.getAttribute("data-map-info");
            updateMap(mapInfo);
        });
    });

    branches.forEach(branch => {
        branch.addEventListener("click", function (e) {
            if (!e.target.classList.contains("show--map--btn")) {
                const mapInfo = this.getAttribute("data-map-info");
                updateMap(mapInfo);
            }
        });
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