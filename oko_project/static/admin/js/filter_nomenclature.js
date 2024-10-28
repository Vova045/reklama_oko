document.addEventListener('DOMContentLoaded', function () {
    const operationSelects = document.querySelectorAll('.operation-select');

    operationSelects.forEach((operationSelect) => {
        operationSelect.addEventListener('change', function () {
            const operationId = this.value;
            const nomenclatureSelect = this.closest('tr').querySelector('.nomenclature-select');

            if (operationId) {
                fetch(`/api/productcomposition/filter_nomenclature/?operation_id=${operationId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Очищаем текущие опции
                        nomenclatureSelect.innerHTML = '<option value="">-- Выберите номенклатуру --</option>';
                        // Добавляем новые опции
                        data.nomenklatura.forEach(nomenclature => {
                            const option = document.createElement('option');
                            option.value = nomenclature.id;
                            option.textContent = nomenclature.name;
                            nomenclatureSelect.appendChild(option);
                        });
                        nomenclatureSelect.disabled = false; // Разблокируем селектор номенклатуры
                    })
                    .catch(error => console.error('Ошибка:', error));
            } else {
                nomenclatureSelect.innerHTML = '<option value="">-- Выберите номенклатуру --</option>';
                nomenclatureSelect.disabled = true; // Блокируем селектор номенклатуры
            }
        });
    });
});
