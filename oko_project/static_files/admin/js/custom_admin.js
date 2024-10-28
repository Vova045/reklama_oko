document.addEventListener('DOMContentLoaded', function() {
    // Создаем новый элемент ссылки
    var customLink = document.createElement('a');
    customLink.href = '/edit-default-parameters/'; // Указываем относительный URL
    customLink.textContent = 'Редактировать параметры по умолчанию'; // Текст ссылки
    customLink.target = '_blank'; // Открывать в новой вкладке

    // Находим элемент, куда мы будем добавлять наш текст
    var adminHeader = document.querySelector('#toolbar');
    if (adminHeader) {
        adminHeader.appendChild(customLink); // Добавляем ссылку
    }
    console.log(customLink.textContent);
});