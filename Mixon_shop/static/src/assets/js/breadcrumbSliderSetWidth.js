function dispatchMaxTranslateEvent() {
    const event = new Event('calculateMaxTranslateEvent');
    document.dispatchEvent(event);
}

function setBreadcrumbWidth() {
    const breadcrumbItems = document.querySelectorAll('.breadcrumb__content--menu__items');
    let totalWidth = 0;

    breadcrumbItems.forEach(function (item) {
        const style = getComputedStyle(item);
        totalWidth += item.offsetWidth + parseInt(style.marginLeft) + parseInt(style.marginRight);
    });

    const breadcrumb = document.querySelector('.breadcrumb__content--menu');
    breadcrumb.style.width = totalWidth + 'px';
    dispatchMaxTranslateEvent();
}

window.addEventListener('load', setBreadcrumbWidth);
window.addEventListener('resize', setBreadcrumbWidth);