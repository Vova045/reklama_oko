document.addEventListener('DOMContentLoaded', function () {
    const formulaItems = document.querySelectorAll('.formula-item');
    const mathSymbols = document.querySelectorAll('.math-symbol');
    const formulaInput = document.querySelector('#id_formula');  // Убедитесь, что это соответствует ID вашего поля "Формула расчета"

    // Обработчик клика для формул
    formulaItems.forEach(item => {
        item.addEventListener('click', function () {
            console.log(formulaInput)
            if (formulaInput) {
                formulaInput.value += this.textContent;
            }
        });
    });

    // Обработчик клика для математических знаков
    mathSymbols.forEach(symbol => {
        symbol.addEventListener('click', function () {
            console.log(formulaInput)
            if (formulaInput) {
                formulaInput.value += this.textContent;
            }
        });
    });
});

