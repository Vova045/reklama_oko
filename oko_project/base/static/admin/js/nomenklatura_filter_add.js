document.addEventListener('DOMContentLoaded', function () {
    applyNomenklaturaForAllFields2();
    document.addEventListener('click', async function(event) {
        const addRowLink2 = event.target.closest('.add-row a');
        if (addRowLink2 && addRowLink2.textContent.includes("Add another Добавочный материал Технологической операции")) {
            console.log('Add another Добавочный материал Технологической операции')
            event.preventDefault();  // Отменяем стандартное поведение
            setTimeout(function() {
                applyNomenklaturaForAllFields2(); // Применяем обработчики к новым элементам
                copyFolderValue2(); // Копируем значение папки из последнего элемента в новый
            }, 100);
        }
    });
});
function applyNomenklaturaForAllFields2() {
    const folderFields2 = document.querySelectorAll('[id^="id_addingmaterialstechnologicaloperation_set-"][id$="-folder"]');
    folderFields2.forEach((folderField_in2, index) => {
        const nomenklaturaField2 = document.querySelector(`#id_addingmaterialstechnologicaloperation_set-${index}-nomenklatura`);
        updateNomenklaturaOptions(folderField_in2, nomenklaturaField2);
        folderField_in2.addEventListener('change', function () {
            updateNomenklaturaOptions2(folderField_in2, nomenklaturaField2);
        });
    });
}
function updateNomenklaturaOptions2(folderField, nomenklaturaField) {
    const folderId2 = folderField.value;
    const selectedValue2 = nomenklaturaField ? nomenklaturaField.value : null;
    if (!nomenklaturaField) {
        return; 
    }
    if (folderId2) {
        fetch(`/get_add_nomenklature_by_folder/${folderId2}/`)
            .then(response => response.json())
            .then(data => {
                if (!nomenklaturaField) return;
                nomenklaturaField.innerHTML = '';
                data.forEach(nomenklatura2 => {
                    const option2 = document.createElement('option');
                    option2.value = nomenklatura2.id;
                    option2.textContent = nomenklatura2.name;
                    if (nomenklatura2.id === selectedValue2) {
                        option2.selected = true;
                    }
                    nomenklaturaField.appendChild(option2);
                });
                nomenklaturaField.value = selectedValue2;
            })
            .catch(error => console.error("Ошибка при получении данных номенклатур:", error));
    } else {
        nomenklaturaField.innerHTML = '';
    }
}
function copyFolderValue2() {
    const folderFields2 = document.querySelectorAll('[id^="id_addingmaterialstechnologicaloperation_set-"][id$="-folder"]');    
    if (folderFields2.length > 1) {
        const visibleFolderFields2 = Array.from(folderFields2).filter(field => field.offsetParent !== null); // Проверяем, что поле отображается
        if (visibleFolderFields2.length > 1) {
            const lastFolderField2 = visibleFolderFields2[visibleFolderFields2.length - 2]; // Предпоследнее поле
            const newFolderField2 = visibleFolderFields2[visibleFolderFields2.length - 1]; // Новое поле
            newFolderField2.value = lastFolderField2.value;
            const nomenklaturaField2 = document.querySelector(`#id_addingmaterialstechnologicaloperation_set-${visibleFolderFields2.length - 1}-nomenklatura`);
            updateNomenklaturaOptions(newFolderField2, nomenklaturaField2);
        }
    } else {
    }
}
