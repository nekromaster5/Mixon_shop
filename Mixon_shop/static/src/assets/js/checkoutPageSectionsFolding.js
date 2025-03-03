const cartTitle = document.getElementById('cart--title');
const cartNextElementButton = document.getElementById('cart--next__action');
const cartEditElementButton = document.getElementById('cart--edit');
const cartItems = document.getElementById('cart--items');
const cartItemsLarge = document.getElementById('cart--items__large');
const contactsTitle = document.getElementById('contacts--title');
const contactsNextElementButton = document.getElementById('contacts--next__action');
const contactsEditElementButton = document.getElementById('contacts--edit');
const contactsItems = document.getElementById('contacts--items');
const contactsItemsLarge = document.getElementById('contacts--items__large');
const contactsNumber = document.getElementById('contacts--number');
const shippingTitle = document.getElementById('shipping--title');
const shippingNextElementButton = document.getElementById('shipping--next__action');
const shippingEditElementButton = document.getElementById('shipping--edit');
const shippingItems = document.getElementById('shipping--items');
const shippingItemsLarge = document.getElementById('shipping--items__large');
const shippingNumber = document.getElementById('shipping--number');
const paymentTitle = document.getElementById('payment--title');
const paymentNextElementButton = document.getElementById('payment--next__action');
const paymentEditElementButton = document.getElementById('payment--edit');
const paymentItems = document.getElementById('payment--items');
const paymentItemsLarge = document.getElementById('payment--items__large');
const paymentNumber = document.getElementById('payment--number');
const commentsTitle = document.getElementById('comments--title');
const commentsNextElementButton = document.getElementById('comments--next__action');
const commentsEditElementButton = document.getElementById('comments--edit');
const commentsItems = document.getElementById('comments--items');
const commentsItemsLarge = document.getElementById('comments--items__large');
const commentsNumber = document.getElementById('comments--number');
const confirmationTitle = document.getElementById('confirmation--title');
const confirmationNextElementButton = document.getElementById('confirmation--next__action');
const confirmationItems = document.getElementById('confirmation--items');
const confirmationItemsLarge = document.getElementById('confirmation--items__large');
const confirmationNumber = document.getElementById('confirmation--number');
let confirmationEditElementButton;


let screenWidth = window.innerWidth;

window.addEventListener('resize', function (event) {
    // Получаем текущие размеры экрана
    screenWidth = window.innerWidth;

    // Проверяем, соответствует ли ширина экрана нашим условиям
    if (screenWidth <= 992) {
        if (cartTitle.classList.contains('checkout__section--folded')) {
            document.querySelector('.section--shipping__address').style.marginTop = '0';
            document.querySelector('.section--shipping__address').style.paddingTop = '4rem';
        }
    } else {
        if (cartTitle.classList.contains('checkout__section--folded')) {
            document.querySelector('.section--shipping__address').style.marginTop = '-18.9rem';
            document.querySelector('.section--shipping__address').style.paddingTop = '0';
        }
    }
});

function paintActive(numberDiv) {
    numberDiv.style.color = 'rgb(255, 0, 0)';
    numberDiv.style.backgroundColor = 'rgb(255, 255, 255)';
}

function paintInactive(numberDiv) {
    numberDiv.style.color = 'rgb(255, 255, 255)';
    numberDiv.style.backgroundColor = 'rgb(174, 173, 170)';
}

function makeDisappear(title, nextElementButton, items, itemsLarge, editElementButton, number) {
    if (title === cartTitle) {
        if (screenWidth >= 992) {
            document.querySelector('.section--shipping__address').style.marginTop = '-18.9rem';
            document.querySelector('.section--shipping__address').style.paddingTop = '0';
        }
    }
    title.classList.add('checkout__section--folded');
    nextElementButton.style.display = 'none';
    if (editElementButton) {
        editElementButton.style.display = 'block';
    }
    items.style.display = 'block';
    itemsLarge.style.display = 'none';
    if (number) {
        paintInactive(number);
    }
}

function makeAppear(title, nextElementButton, items, itemsLarge, editElementButton, number) {
    if (title === cartTitle) {
        document.querySelector('.section--shipping__address').style.marginTop = '0';
        document.querySelector('.section--shipping__address').style.paddingTop = '4rem';
    }
    title.classList.remove('checkout__section--folded');
    nextElementButton.style.display = 'block';
    if (editElementButton) {
        editElementButton.style.display = 'none';
    }
    items.style.display = 'none';
    itemsLarge.style.display = 'block';
    if (number) {
        paintActive(number);
    }
}

function activateCart() {
    makeAppear(cartTitle, cartNextElementButton, cartItems, cartItemsLarge, cartEditElementButton,);
    makeDisappear(contactsTitle, contactsNextElementButton, contactsItems, contactsItemsLarge, contactsEditElementButton, contactsNumber);
    makeDisappear(shippingTitle, shippingNextElementButton, shippingItems, shippingItemsLarge, shippingEditElementButton, shippingNumber);
    makeDisappear(paymentTitle, paymentNextElementButton, paymentItems, paymentItemsLarge, paymentEditElementButton, paymentNumber);
    makeDisappear(commentsTitle, commentsNextElementButton, commentsItems, commentsItemsLarge, commentsEditElementButton, commentsNumber);
    makeDisappear(confirmationTitle, confirmationNextElementButton, confirmationItems, confirmationItemsLarge, null, confirmationNumber);
}

function activateContacts() {
    makeDisappear(cartTitle, cartNextElementButton, cartItems, cartItemsLarge, cartEditElementButton,);
    makeAppear(contactsTitle, contactsNextElementButton, contactsItems, contactsItemsLarge, contactsEditElementButton, contactsNumber);
    makeDisappear(shippingTitle, shippingNextElementButton, shippingItems, shippingItemsLarge, shippingEditElementButton, shippingNumber);
    makeDisappear(paymentTitle, paymentNextElementButton, paymentItems, paymentItemsLarge, paymentEditElementButton, paymentNumber);
    makeDisappear(commentsTitle, commentsNextElementButton, commentsItems, commentsItemsLarge, commentsEditElementButton, commentsNumber);
    makeDisappear(confirmationTitle, confirmationNextElementButton, confirmationItems, confirmationItemsLarge, null, confirmationNumber);
}

function activateShipping() {
    makeDisappear(cartTitle, cartNextElementButton, cartItems, cartItemsLarge, cartEditElementButton,);
    makeDisappear(contactsTitle, contactsNextElementButton, contactsItems, contactsItemsLarge, contactsEditElementButton, contactsNumber);
    makeAppear(shippingTitle, shippingNextElementButton, shippingItems, shippingItemsLarge, shippingEditElementButton, shippingNumber);
    makeDisappear(paymentTitle, paymentNextElementButton, paymentItems, paymentItemsLarge, paymentEditElementButton, paymentNumber);
    makeDisappear(commentsTitle, commentsNextElementButton, commentsItems, commentsItemsLarge, commentsEditElementButton, commentsNumber);
    makeDisappear(confirmationTitle, confirmationNextElementButton, confirmationItems, confirmationItemsLarge, null, confirmationNumber);
    document.dispatchEvent(calculateMaxTranslateEvent);
}

function activatePayment() {
    makeDisappear(cartTitle, cartNextElementButton, cartItems, cartItemsLarge, cartEditElementButton,);
    makeDisappear(contactsTitle, contactsNextElementButton, contactsItems, contactsItemsLarge, contactsEditElementButton, contactsNumber);
    makeDisappear(shippingTitle, shippingNextElementButton, shippingItems, shippingItemsLarge, shippingEditElementButton, shippingNumber);
    makeAppear(paymentTitle, paymentNextElementButton, paymentItems, paymentItemsLarge, paymentEditElementButton, paymentNumber);
    makeDisappear(commentsTitle, commentsNextElementButton, commentsItems, commentsItemsLarge, commentsEditElementButton, commentsNumber);
    makeDisappear(confirmationTitle, confirmationNextElementButton, confirmationItems, confirmationItemsLarge, null, confirmationNumber);
    document.dispatchEvent(calculateMaxTranslateEvent);
}

function activateComments() {
    makeDisappear(cartTitle, cartNextElementButton, cartItems, cartItemsLarge, cartEditElementButton,);
    makeDisappear(contactsTitle, contactsNextElementButton, contactsItems, contactsItemsLarge, contactsEditElementButton, contactsNumber);
    makeDisappear(shippingTitle, shippingNextElementButton, shippingItems, shippingItemsLarge, shippingEditElementButton, shippingNumber);
    makeDisappear(paymentTitle, paymentNextElementButton, paymentItems, paymentItemsLarge, paymentEditElementButton, paymentNumber);
    makeAppear(commentsTitle, commentsNextElementButton, commentsItems, commentsItemsLarge, commentsEditElementButton, commentsNumber);
    makeDisappear(confirmationTitle, confirmationNextElementButton, confirmationItems, confirmationItemsLarge, null, confirmationNumber);
}

function activateConfirmation() {
    makeDisappear(cartTitle, cartNextElementButton, cartItems, cartItemsLarge, cartEditElementButton,);
    makeDisappear(contactsTitle, contactsNextElementButton, contactsItems, contactsItemsLarge, contactsEditElementButton, contactsNumber);
    makeDisappear(shippingTitle, shippingNextElementButton, shippingItems, shippingItemsLarge, shippingEditElementButton, shippingNumber);
    makeDisappear(paymentTitle, paymentNextElementButton, paymentItems, paymentItemsLarge, paymentEditElementButton, paymentNumber);
    makeDisappear(commentsTitle, commentsNextElementButton, commentsItems, commentsItemsLarge, commentsEditElementButton, commentsNumber);
    makeAppear(confirmationTitle, confirmationNextElementButton, confirmationItems, confirmationItemsLarge, null, confirmationNumber);
}

cartEditElementButton.addEventListener('click', activateCart);
cartNextElementButton.addEventListener('click', activateContacts);
contactsEditElementButton.addEventListener('click', activateContacts);
contactsNextElementButton.addEventListener('click', activateShipping);
contactsNextElementButton.addEventListener('click', function () {
    document.querySelectorAll(".span_name").forEach(element => {
    element.textContent = document.getElementById("input_name").value;});
    document.querySelectorAll(".span_phone").forEach(element => {
    element.textContent = document.getElementById("input_phone").value;});
    document.querySelectorAll(".span_email").forEach(element => {
    element.textContent = document.getElementById("input_email").value;});
});
shippingEditElementButton.addEventListener('click', activateShipping);
shippingNextElementButton.addEventListener('click', activatePayment);
shippingNextElementButton.addEventListener('click', function () {
    document.querySelectorAll(".span_city").forEach(element => {
    element.textContent =
        document.getElementById("input_city").options[document.getElementById("input_city").selectedIndex].text;});

    let activeShippingButton = document.querySelector(".shipment__page--list--item.shipping.active");
    if (activeShippingButton) {
        document.querySelectorAll(".span_shipment-method").forEach(element => {
    element.textContent =
            activeShippingButton.querySelector(".shipment__method--type__description").textContent;});
    } else {
        document.querySelectorAll(".span_shipment-method").forEach(element => {
    element.textContent = "Способ доставки не выбран";});
    }
});
paymentEditElementButton.addEventListener('click', activatePayment);
paymentNextElementButton.addEventListener('click', activateComments);
paymentNextElementButton.addEventListener('click', function () {
    let activePaymentButton = document.querySelector(".shipment__page--list--item.payment.active");
    if (activePaymentButton) {
        document.querySelectorAll(".span_payment-method").forEach(element => {
    element.textContent =
            activePaymentButton.querySelector(".shipment__method--type__description").textContent;});
    } else {
        document.querySelectorAll(".span_payment-method").forEach(element => {
    element.textContent = "Способ оплаты не выбран";});
    }
});
commentsEditElementButton.addEventListener('click', activateComments);
commentsNextElementButton.addEventListener('click', activateConfirmation);
commentsNextElementButton.addEventListener('click', function () {
    let text_comment = document.getElementById("text_comment").value;
    if (text_comment) {
        document.querySelectorAll(".span_comments").forEach(element => {
    element.textContent = text_comment});
    } else {
        document.querySelectorAll(".span_comments").forEach(element => {
    element.textContent = "Комментариев нет"});
    }

});
