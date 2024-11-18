document.addEventListener('DOMContentLoaded', function () {
    applyProductionOperationForAllFields();
    document.addEventListener('click', async function(event) {
        const addRowLink1 = event.target.closest('.add-row a');
        if (addRowLink1 && addRowLink1.textContent.includes("Add another Операция внутри Технологической операции")) {
            console.log('Add another Операция внутри Технологической операции')
            event.preventDefault();
            setTimeout(function() {
                applyProductionOperationForAllFields();
                copyFolderValue3();
            }, 100); 
        }
    });
});
function applyProductionOperationForAllFields() {
    const folderFields3 = document.querySelectorAll('[id^="id_operationoftechnologicaloperation_set-"][id$="-folder"]');
    folderFields3.forEach((folderField_in3, index) => {
        const productionOperationField = document.querySelector(`#id_operationoftechnologicaloperation_set-${index}-production_operation`);
        updateProductionOperationOptions(folderField_in3, productionOperationField);
        folderField_in3.addEventListener('change', function () {
            updateProductionOperationOptions(folderField_in3, productionOperationField);
        });

    });
}
function updateProductionOperationOptions(folderField, productionOperationField) {
    const folderId3 = folderField.value;
    const selectedValue3 = productionOperationField ? productionOperationField.value : null;
    if (!productionOperationField) {
        return; 
    }
    if (folderId3) {
        fetch(`/get_production_operation_by_folder/${folderId3}/`)
            .then(response => response.json())
            .then(data => {
                if (!productionOperationField) return;
                    productionOperationField.innerHTML = '';  // Очистка предыдущих значений
                    data.forEach(productionOperation => {
                        const option3 = document.createElement('option');
                        option3.value = productionOperation.id;
                        option3.textContent = productionOperation.name;
                        if (productionOperation.id === selectedValue3) {
                            option3.selected = true;
                        }
                        productionOperationField.appendChild(option3);
                    });
                    productionOperationField.value = selectedValue3;
            })
            .catch(error => console.error("Ошибка при получении данных:", error));
    } else {
        if (productionOperationField) {
            productionOperationField.innerHTML = ''; // Очистка при отсутствии folderId3
        }
    }
}

function copyFolderValue3() {
    const folderFields3 = document.querySelectorAll('[id^="id_operationoftechnologicaloperation_set-"][id$="-folder"]');
    if (folderFields3.length > 1) {
        const visibleFolderFields3 = Array.from(folderFields3).filter(field => field.offsetParent !== null);
        if (visibleFolderFields3.length > 1) {
            const lastFolderField3 = visibleFolderFields3[visibleFolderFields3.length - 2];
            const newFolderField3 = visibleFolderFields3[visibleFolderFields3.length - 1];
            newFolderField3.value = lastFolderField3.value;
            const productionOperationField3 = document.querySelector(`#id_operationoftechnologicaloperation_set-${visibleFolderFields3.length - 1}-production_operation`);
            updateProductionOperationOptions(newFolderField3, productionOperationField3);
        }
    }
}
