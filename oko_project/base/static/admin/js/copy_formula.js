document.addEventListener('DOMContentLoaded', function () {
    initFormulaClickHandlers(); // Вызываем при загрузке страницы для начальных символов
});

// Функция для добавления обработчиков кликов
function initFormulaClickHandlers() {
    const formulaItems = document.querySelectorAll('.formula-item');
    const mathSymbols = document.querySelectorAll('.math-symbol');
    const formulaInput = document.querySelector('#id_formula');  // ID поля "Формула расчета"

    // Обработчик клика для формул
    formulaItems.forEach(item => {
        item.addEventListener('click', function () {
            if (formulaInput) {
                formulaInput.value += this.textContent;
            }
        });
    });

    // Обработчик клика для математических знаков
    mathSymbols.forEach(symbol => {
        symbol.addEventListener('click', function () {
            if (formulaInput) {
                formulaInput.value += this.textContent;
            }
        });
    });
}
