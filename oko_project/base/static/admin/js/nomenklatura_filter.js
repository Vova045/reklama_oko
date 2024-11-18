document.addEventListener('DOMContentLoaded', function () {
    applyNomenklaturaForAllFields();
    document.addEventListener('click', async function(event) {
        const addRowLink3 = event.target.closest('.add-row a');
        if (addRowLink3 && addRowLink3.textContent.includes("Add another Материал технологической операции")) {
            console.log('Add another Материал технологической операции')
            event.preventDefault();  // Отменяем стандартное поведение
            setTimeout(function() {
                applyNomenklaturaForAllFields(); // Применяем обработчики к новым элементам
                copyFolderValue(); // Копируем значение папки из последнего элемента в новый
            }, 100);
        }
    });
});
function applyNomenklaturaForAllFields() {
    const folderFields = document.querySelectorAll('[id^="id_materialstechnologicaloperation_set-"][id$="-folder"]');
    folderFields.forEach((folderField_in, index) => {
        const nomenklaturaField = document.querySelector(`#id_materialstechnologicaloperation_set-${index}-nomenklatura`);
        updateNomenklaturaOptions(folderField_in, nomenklaturaField);
        folderField_in.addEventListener('change', function () {
            updateNomenklaturaOptions(folderField_in, nomenklaturaField);
        });
    });
}
function updateNomenklaturaOptions(folderField, nomenklaturaField) {
    const folderId = folderField.value;
    const selectedValue = nomenklaturaField ? nomenklaturaField.value : null;
    if (!nomenklaturaField) {
        return; 
    }
    if (folderId) {
        fetch(`/get_nomenklatura_by_folder/${folderId}/`)
            .then(response => response.json())
            .then(data => {
                if (!nomenklaturaField) return;
                nomenklaturaField.innerHTML = '';  
                data.forEach(nomenklatura => {
                    const option = document.createElement('option');
                    option.value = nomenklatura.id;
                    option.textContent = nomenklatura.name;                    
                    if (nomenklatura.id === selectedValue) {
                        option.selected = true;
                    }
                    nomenklaturaField.appendChild(option);
                });
                nomenklaturaField.value = selectedValue;
            })
            .catch(error => console.error("Ошибка при получении данных номенклатур:", error));
    } else {
        nomenklaturaField.innerHTML = '';
    }
}

function copyFolderValue() {
    const folderFields = document.querySelectorAll('[id^="id_materialstechnologicaloperation_set-"][id$="-folder"]');
    if (folderFields.length > 1) {
        const visibleFolderFields = Array.from(folderFields).filter(field => field.offsetParent !== null); // Проверяем, что поле отображается
        if (visibleFolderFields.length > 1) {
            const lastFolderField = visibleFolderFields[visibleFolderFields.length - 2]; // Предпоследнее поле
            const newFolderField = visibleFolderFields[visibleFolderFields.length - 1]; // Новое поле
            newFolderField.value = lastFolderField.value;
            const nomenklaturaField = document.querySelector(`#id_materialstechnologicaloperation_set-${visibleFolderFields.length - 1}-nomenklatura`);
            updateNomenklaturaOptions(newFolderField, nomenklaturaField);
        }
    } else {
    }
}
