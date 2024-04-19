  // Функция увеличения и уменьшения значения счетчика
  function adjustCounter(input, increase) {
    let value = parseInt(input.value, 10);
    value = isNaN(value) ? 1 : increase ? value + 1 : Math.max(1, value - 1);
    input.value = value;
  }

  // Назначаем обработчики для каждой кнопки в каждом счетчике
  document.querySelectorAll('.product--amount').forEach(counter => {
    const numberInput = counter.querySelector('.product--amount__input');

    counter.querySelector('#increase').addEventListener('click', () => adjustCounter(numberInput, true));
    counter.querySelector('#decrease').addEventListener('click', () => adjustCounter(numberInput, false));

    numberInput.addEventListener('change', () => {
      let value = parseInt(numberInput.value, 10);
      numberInput.value = isNaN(value) || value < 1 ? 1 : value;
    });
  });