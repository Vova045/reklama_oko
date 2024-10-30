BX.ready(function() {
    // Находим кнопку "Создать сделку"
    var createDealButton = document.querySelector('button[data-id="create"]'); // Пожалуйста, проверьте правильный селектор

    if (createDealButton) {
        // Создаем новый элемент ссылки
        var appLink = document.createElement('a');
        appLink.href = 'https://reklamaoko.ru'; // Ссылка на ваше приложение
        appLink.innerText = 'Запустить приложение'; // Текст ссылки
        appLink.style.marginLeft = '10px'; // Добавляем отступ
        appLink.style.color = '#007bff'; // Задаем цвет ссылки
        appLink.style.textDecoration = 'underline'; // Подчеркиваем текст
        appLink.style.cursor = 'pointer'; // Изменяем курсор на указатель

        // Вставляем ссылку рядом с кнопкой "Создать сделку"
        createDealButton.parentNode.insertBefore(appLink, createDealButton.nextSibling);
    }
});
