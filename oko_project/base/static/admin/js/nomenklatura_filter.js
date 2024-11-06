document.addEventListener('DOMContentLoaded', function () {
    // Применяем функцию ко всем существующим элементам при загрузке страницы
    applyNomenklaturaForAllFields();

    // Добавляем обработчик на клик по "Add another" для динамического добавления полей
    document.addEventListener('click', async function(event) {
        if (event.target.closest('.add-row a')) {
            console.log("Клик по кнопке добавления новой строки.");
            event.preventDefault();  // Отменяем стандартное поведение

            // Ждём немного, чтобы новые элементы появились в DOM
            setTimeout(function() {
                applyNomenklaturaForAllFields();
            }, 100);
        }
    });
});

// Функция для применения обработчиков ко всем полям
function applyNomenklaturaForAllFields() {
    const folderFields = document.querySelectorAll('[id^="id_materialstechnologicaloperation_set-"][id$="-folder"]');
    folderFields.forEach((folderField, index) => {
        const nomenklaturaField = document.querySelector(`#id_materialstechnologicaloperation_set-${index}-nomenklatura`);

        // Изначально применяем фильтрацию при загрузке страницы
        updateNomenklaturaOptions(folderField, nomenklaturaField);

        // Обновляем фильтрацию при изменении папки
        folderField.addEventListener('change', function () {
            updateNomenklaturaOptions(folderField, nomenklaturaField);
        });
    });
}

// Функция для обновления списка номенклатур в зависимости от выбранной папки
function updateNomenklaturaOptions(folderField, nomenklaturaField) {
    const folderId = folderField.value;

    if (folderId) {
        // Отправляем запрос на сервер, чтобы получить номенклатуры для выбранной папки
        fetch(`/get_nomenklatura_by_folder/${folderId}/`)
            .then(response => response.json())
            .then(data => {
                // Очищаем старые опции
                nomenklaturaField.innerHTML = '';  

                // Добавляем новые опции
                data.forEach(nomenklatura => {
                    const option = document.createElement('option');
                    option.value = nomenklatura.id;
                    option.textContent = nomenklatura.name;
                    nomenklaturaField.appendChild(option);
                });
            });
    } else {
        // Если папка не выбрана, очищаем поле номенклатуры
        nomenklaturaField.innerHTML = '';
    }
}
