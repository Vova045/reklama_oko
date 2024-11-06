document.addEventListener('DOMContentLoaded', function () {
    // Изначально применяем функцию ко всем существующим элементам
    applyNomenklaturaForAllFields();

    // Добавляем обработчик на клик по "Add another" для динамического добавления полей
    document.addEventListener('click', async function(event) {
        if (event.target.closest('.add-row a')) {
            console.log("Клик по кнопке добавления новой строки.");
            event.preventDefault();  // Отменяем стандартное поведение

            // Нужно немного подождать, чтобы новые элементы были добавлены в DOM
            setTimeout(function() {
                applyNomenklaturaForAllFields();
            }, 100);
        }
    });

    // Применяем обработчик для изменения папки
    const folderFields = document.querySelectorAll('[id$="-folder"]');
    folderFields.forEach(folderField => {
        folderField.addEventListener('change', function () {
            const folderId = folderField.value;
            const nomenklaturaField = folderField.closest('form').querySelector('[id$="-nomenklatura"]');
            
            if (folderId) {
                // Отправляем запрос на сервер, чтобы получить номенклатуры для выбранной папки
                fetch(`/get_nomenklatura_by_folder/${folderId}/`)
                    .then(response => response.json())
                    .then(data => {
                        // Обновляем список номенклатур
                        const nomenklaturaOptions = nomenklaturaField.querySelectorAll('option');
                        nomenklaturaOptions.forEach(option => option.remove());

                        data.forEach(nomenklatura => {
                            const option = document.createElement('option');
                            option.value = nomenklatura.id;
                            option.textContent = nomenklatura.name;
                            nomenklaturaField.appendChild(option);
                        });
                    });
            }
        });
    });
});

// Функция для применения обработчиков ко всем полям
function applyNomenklaturaForAllFields() {
    const folderFields = document.querySelectorAll('[id^="id_materialstechnologicaloperation_set-"][id$="-folder"]');
    folderFields.forEach((folderField, index) => {
        const folderSelector = `#id_materialstechnologicaloperation_set-${index}-folder`;
        const nomenklaturaSelector = `#id_materialstechnologicaloperation_set-${index}-nomenklatura`;

        updateNomenklaturaField(folderSelector, nomenklaturaSelector);
    });
}

// Функция для обновления поля номенклатуры на основе выбранной папки
function updateNomenklaturaField(folderSelector, nomenklaturaSelector) {
    const folderField = document.querySelector(folderSelector);
    const nomenklaturaField = document.querySelector(nomenklaturaSelector);

    if (folderField) {
        folderField.addEventListener('change', function () {
            const folderId = folderField.value;
            
            if (folderId) {
                // Отправляем запрос на сервер для получения номенклатур для выбранной папки
                fetch(`/get_nomenklatura_by_folder/${folderId}/`)
                    .then(response => response.json())
                    .then(data => {
                        // Обновляем список номенклатур
                        const nomenklaturaOptions = nomenklaturaField.querySelectorAll('option');
                        nomenklaturaOptions.forEach(option => option.remove());

                        data.forEach(nomenklatura => {
                            const option = document.createElement('option');
                            option.value = nomenklatura.id;
                            option.textContent = nomenklatura.name;
                            nomenklaturaField.appendChild(option);
                        });
                    });
            }
        });
    }
}
