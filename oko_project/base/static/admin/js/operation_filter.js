document.addEventListener('DOMContentLoaded', function () {
    applyTechProductionOperationForAllFields();
    document.addEventListener('click', async function(event) {
        const addRowLink4 = event.target.closest('.add-row a');
        if (addRowLink4 && addRowLink4.textContent.includes("Add another Состав технологического узла")) {
            console.log('Add another Состав технологического узла')
            event.preventDefault();
            setTimeout(function() {
                applyTechProductionOperationForAllFields();
                copyFolderValue4();
            }, 100); 
        }
    });
});

function applyTechProductionOperationForAllFields() {
    const folderFields4 = document.querySelectorAll('[id^="id_technologicallinkcomposition_set-"][id$="-folder"]');
    folderFields4.forEach((folderField_in4, index) => {
            const tech_productionTechOperationField = document.querySelector(`#id_technologicallinkcomposition_set-${index}-technical_operation`);
            updateTechProductionOperationOptions(folderField_in4, tech_productionTechOperationField);
            folderField_in4.addEventListener('change', function () {
                updateTechProductionOperationOptions(folderField_in4, tech_productionTechOperationField);
            });

    });
}


function updateTechProductionOperationOptions(folderField4, productionTechOperationField) {
    console.log('updateTechProductionOperationOptions')
    const folderId4 = folderField4.value;
    const selectedValue4 = productionTechOperationField ? productionTechOperationField.value : null;
    if (!productionTechOperationField) {
        return; 
    }
    if (folderId4) {
        console.log('updateTechProductionOperationOptions-2')
        fetch(`/get_technical_operations_by_folder/${folderId4}/`)
            .then(response => response.json())
            .then(data => {
                if (!productionTechOperationField) return;
                productionTechOperationField.innerHTML = '';
                data.forEach(techproductionOperation => {
                    const option4 = document.createElement('option');
                    option4.value = techproductionOperation.id;
                    option4.textContent = techproductionOperation.name;
                    console.log(option4.textContent)
                    if (techproductionOperation.id === selectedValue4) {
                        option4.selected = true;
                        console.log('выбран')
                        console.log(option4.textContent)
                    }
                    productionTechOperationField.appendChild(option4);
                });
                productionTechOperationField.value = selectedValue4;
            })
            .catch(error => console.error("Ошибка при загрузке операций:", error));
    } else {
        if (productionTechOperationField) {
            productionTechOperationField.innerHTML = ''; // Очистка при отсутствии folderId3
        }
    }
}

function copyFolderValue4() {
    const folderFields4 = document.querySelectorAll('[id^="id_technologicallinkcomposition_set-"][id$="-folder"]');
    if (folderFields4.length > 1) {
        const visibleFolderFields4 = Array.from(folderFields4).filter(field => field.offsetParent !== null);
        if (visibleFolderFields4.length > 1) {
            const lastFolderField4 = visibleFolderFields4[visibleFolderFields4.length - 2];
            const newFolderField4 = visibleFolderFields4[visibleFolderFields4.length - 1];
            newFolderField4.value = lastFolderField4.value;
            const productionTechOperationField4 = document.querySelector(`#id_technologicallinkcomposition_set-${visibleFolderFields4.length - 1}-technical_operation`);
            updateTechProductionOperationOptions(newFolderField4, productionTechOperationField4);
        }
    }
}
