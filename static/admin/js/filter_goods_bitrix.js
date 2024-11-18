document.addEventListener('DOMContentLoaded', function () {
    console.log("DOMContentLoaded: Применяем фильтр для всех полей...");
    applyFolderFilterForAllFields();
    
    // Проверим, что клик работает
    document.addEventListener('click', async function(event) {
        const addRowLink = event.target.closest('.add-row a');
        if (addRowLink) {
            console.log('Клик на элементе:', addRowLink.textContent);  // Проверяем, что клик на нужной ссылке
        }
        
        if (addRowLink && addRowLink.textContent.includes("Add another Состав товара")) {
            console.log('Клик на "Add another Состав товара"');
            event.preventDefault();  // Отменяем стандартное поведение
            
            setTimeout(function() {
                console.log('Применяем обработчики для новых элементов');
                applyFolderFilterForAllFields(); // Применяем обработчики к новым элементам
                copyFolderValue(); // Копируем значение папки из последнего элемента в новый
            }, 100);
        }
    });
});

// Массив для хранения начальных значений номенклатуры
let initialNomenclatureValues = [];

function applyFolderFilterForAllFields() {
    const folderSelectTechnology = document.querySelectorAll('[id^="id_bitrix_goodscomposition_set-"][id$="-folder_technology"]');
    console.log('Применяем фильтр для папок, найдено:', folderSelectTechnology.length, 'элементов.');

    folderSelectTechnology.forEach((folderSelectTechnology_in, index) => {
        const technologyField = document.querySelector(`#id_bitrix_goodscomposition_set-${index}-technology`);
        const techOperationField = document.querySelector(`#id_bitrix_goodscomposition_set-${index}-techoperation`);
        const folderField = document.querySelector(`#id_bitrix_goodscomposition_set-${index}-folder_technology`);
        const nomenclatureField = document.querySelector(`#id_bitrix_goodscomposition_set-${index}-nomenclature`);

        console.log(`Обрабатываем поле с индексом ${index}`);

        // Сохраняем начальное значение номенклатуры
        if (nomenclatureField && initialNomenclatureValues[index] === undefined) {
            initialNomenclatureValues[index] = nomenclatureField.value;
        }

        // При загрузке страницы обновляем папку для выбранного узла
        if (technologyField) {
            console.log(`Технологическое поле найдено для индекса ${index}.`);

            // При загрузке страницы обновляем папку для выбранного узла
            if (technologyField.value) {
                console.log(`Значение технологии для индекса ${index}: ${technologyField.value}`);
                updateFolderForTechnology(technologyField.value, folderField, techOperationField, index);
            }

            // При изменении выбранного узла, обновляем папку
            technologyField.addEventListener('change', function () {
                const selectedTechId = technologyField.value;
                console.log(`Технология изменена на ID: ${selectedTechId}`);
                updateFolderForTechnology(selectedTechId, folderField, techOperationField, index);  // Обновляем папку для нового узла
                updateTechOperationOptions(selectedTechId, techOperationField, index);
            });
        }

        // Обновляем список технологий при изменении папки
        folderSelectTechnology_in.addEventListener('change', function () {
            console.log(`Изменена папка для индекса ${index}, обновляем список технологий.`);
            updateFieldOptions(folderSelectTechnology_in, technologyField, 'technology');
        });
    });

    // В конце применяем начальные значения для полей номенклатуры
    setTimeout(() => {
        initialNomenclatureValues.forEach((value, index) => {
            const nomenclatureField = document.querySelector(`#id_bitrix_goodscomposition_set-${index}-nomenclature`);
            if (nomenclatureField && value) {
                nomenclatureField.value = value; // Устанавливаем начальное значение
            }
        });
    }, 200);
}

function updateFolderForTechnology(technologyId, folderField, techOperationField, index) {
    if (!technologyId || !folderField) return;

    const technologyField = document.querySelector(`#id_bitrix_goodscomposition_set-${index}-technology`);
    if (!technologyField) {
        console.error(`Не найдено поле технологии для индекса ${index}`);
        return;
    }

    console.log(`Обновляем папку для технологии с ID ${technologyId}`);

    fetch(`/api/get_folder_name_by_technology/?technology_id=${technologyId}`)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data.folder_name) {
                console.log(`Получена папка: ${data.folder_name}`);
                // Перебираем все опции в поле выбора папки
                const options = folderField.querySelectorAll('option');
                console.log(options)
                console.log('Доступные опции для выбора папки:', options.length);
                options.forEach(option => {
                    if (String(option.value) === String(data.folder_id)) {
                        console.log(`Выбрана папка: ${data.folder_name}`);
                        option.selected = true;  // Устанавливаем папку как выбранную
                    } else {
                        option.selected = false;  // Снимаем выбор с других опций
                    }
                });

                // Теперь обновляем список технологий для этой папки
                updateFieldOptions(folderField, technologyField, 'technology');
                updateTechOperationOptions(technologyId, techOperationField, index); // Обновление техопераций
            } else {
                console.log(`Не удалось найти папку для узла с ID: ${technologyId}`);
            }
        })
        .catch(error => console.error("Ошибка при обновлении папки:", error));
}

// Функция для обновления опций в полях технологий
function updateFieldOptions(folderField, field, fieldName) {
    const folderId = folderField.value;
    const selectedValue = field ? field.value : null;
    console.log(`Обновляем опции для поля ${fieldName}, папка ID: ${folderId}, выбранное значение: ${selectedValue}`);
    
    if (!field || !folderId) return;

    fetch(`/api/get_filtered_fields/?folder_id=${folderId}&field_name=${fieldName}`)
        .then(response => response.json())
        .then(data => {
            if (!field) return;
            console.log('Получены данные для обновления опций:', data);
            field.innerHTML = '';  // Очищаем предыдущие опции
            data.options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.id;
                optionElement.textContent = option.operation_link_name || option.operation_name || option.name;
                if (option.id === selectedValue) {
                    optionElement.selected = true;
                }
                field.appendChild(optionElement);
            });
            field.value = selectedValue;
        })
        .catch(error => console.error("Ошибка при получении данных:", error));
}

function updateTechOperationOptions(technologyId, techOperationField, index) {
    if (!technologyId || !techOperationField) return;

    console.log(`Обновляем опции для техопераций, технология ID: ${technologyId}`);
    // Сохраняем текущее значение поля техоперации
    const previousSelectedValue = techOperationField.value;
    console.log(`Выбранная техоперация до обновления: ${previousSelectedValue}`);

    fetch(`/api/get_technology_of_goods/?technology_id=${technologyId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Получены данные для техопераций:', data);

            // Очищаем предыдущее содержимое поля
            techOperationField.innerHTML = '';  
            
            // Добавляем новые опции
            data.operations.forEach(operation => {
                const optionElement = document.createElement('option');
                optionElement.value = operation.id;
                optionElement.textContent = operation.operation_link_name;
                console.log(operation.id )
                console.log(operation.operation_link_name )
                // Если это значение соответствует предыдущему выбранному, делаем его выбранным
                if (String(operation.id) === String(previousSelectedValue)) {
                    optionElement.selected = true;
                }
                techOperationField.appendChild(optionElement);
            });

            // После обновления операций, если есть выбранная операция, обновляем список номенклатуры
            const selectedTechOpId = techOperationField.value;
            console.log(`Выбранная техоперация после обновления: ${selectedTechOpId}`);
            if (selectedTechOpId) {
                sendTechOpToServer(selectedTechOpId, index);
            }
        })
        .catch(error => console.error("Ошибка при загрузке техопераций:", error));
}

// Функция для отправки выбранной технологической операции на сервер
function sendTechOpToServer(techOpId, index) {
    console.log(`Отправка данных по технологической операции ID: ${techOpId}, индекс: ${index}`);

    fetch(`/api/get_nomenclature_by_techoperation/?tech_operation_id=${techOpId}`)
        .then(response => response.json())
        .then(data => {
            console.log("Номенклатура для выбранной технологической операции:", data);  // Для отладки
            updateNomenclatureOptions(data.options, index);  // Обновляем номенклатуру на клиенте
        })
        .catch(error => console.error("Ошибка при отправке данных технологической операции:", error));
}

// Функция для обновления списка номенклатуры на клиенте
function updateNomenclatureOptions(options, index) {
    console.log(`Обновляем номенклатуру для индекса ${index}, найдено ${options.length} опций.`);
    
    // Находим только нужное поле по индексу
    const nomenclatureField = document.querySelector(`#id_bitrix_goodscomposition_set-${index}-nomenclature`);
    console.log(nomenclatureField);

    // Если поле найдено, очищаем его и добавляем новые опции
    if (nomenclatureField) {
        console.log(`Обновляем номенклатуру для поля с индексом ${index}`);
        nomenclatureField.innerHTML = '';  // Очищаем предыдущие опции
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.id;
            optionElement.textContent = option.nomenklatura_name;
            nomenclatureField.appendChild(optionElement);
        });
    } else {
        console.log(`Не найдено поле номенклатуры для индекса ${index}`);
    }
}

function copyFolderValue() {
    // Находим все поля папок, соответствующие составу товара
    const folderFields = document.querySelectorAll('[id^="id_bitrix_goodscomposition_set-"][id$="-folder_technology"]');
    
    if (folderFields.length > 1) {
        // Фильтруем только видимые поля
        const visibleFolderFields = Array.from(folderFields).filter(field => field.offsetParent !== null);
        
        if (visibleFolderFields.length > 1) {
            // Получаем индексы предпоследнего и последнего поля
            const lastIndex = visibleFolderFields.length - 2; // Предпоследнее поле
            const newIndex = visibleFolderFields.length - 1; // Новое поле
            
            // Находим все связанные поля
            const lastFields = {
                folder: document.querySelector(`#id_bitrix_goodscomposition_set-${lastIndex}-folder_technology`),
                technology: document.querySelector(`#id_bitrix_goodscomposition_set-${lastIndex}-technology`),
                techOperation: document.querySelector(`#id_bitrix_goodscomposition_set-${lastIndex}-techoperation`),
                nomenclature: document.querySelector(`#id_bitrix_goodscomposition_set-${lastIndex}-nomenclature`),
            };
            
            const newFields = {
                folder: document.querySelector(`#id_bitrix_goodscomposition_set-${newIndex}-folder_technology`),
                technology: document.querySelector(`#id_bitrix_goodscomposition_set-${newIndex}-technology`),
                techOperation: document.querySelector(`#id_bitrix_goodscomposition_set-${newIndex}-techoperation`),
                nomenclature: document.querySelector(`#id_bitrix_goodscomposition_set-${newIndex}-nomenclature`),
            };

            // Проверяем, что все поля найдены
            if (lastFields.folder && newFields.folder) {
                // Копируем значения из предпоследнего элемента в новый
                newFields.folder.value = lastFields.folder.value;
                console.log(`Копируем папку: ${lastFields.folder.value}`);
            }

            if (lastFields.technology && newFields.technology) {
                newFields.technology.value = lastFields.technology.value;
                console.log(`Копируем технологию: ${lastFields.technology.value}`);
            }

            if (lastFields.techOperation && newFields.techOperation) {
                newFields.techOperation.value = lastFields.techOperation.value;
                console.log(`Копируем техоперацию: ${lastFields.techOperation.value}`);
            }

            if (lastFields.nomenclature && newFields.nomenclature) {
                newFields.nomenclature.value = lastFields.nomenclature.value;
                console.log(`Копируем номенклатуру: ${lastFields.nomenclature.value}`);
            }

            // Вызываем обновления, если это необходимо
            if (newFields.folder && newFields.technology) {
                updateFieldOptions(newFields.folder, newFields.technology, 'technology');
            }
            if (newFields.technology && newFields.techOperation) {
                updateTechOperationOptions(newFields.technology.value, newFields.techOperation, newIndex);
            }
        }
    } else {
        console.log("Недостаточно полей для копирования значения папки.");
    }
}
