<?php
// Настройки приложения
$clientId = 'local.671fe1a5771b80.36776378';
$clientSecret = 'rxXLQH8AI2Ig9Uvgx7VmcsVKD39Qs46vIMiRGZiu2GsxHrAfE2';
$redirectUri = 'https://reklamaoko.ru/static/button_handler.php';

// Функция для логирования
function logMessage($message) {
    file_put_contents('log.txt', date('Y-m-d H:i:s') . " - $message" . PHP_EOL, FILE_APPEND);
}

// Получение входных данных
$input = file_get_contents('php://input');
$data = json_decode($input, true);

// Лог входных данных
logMessage("Получен входной запрос: " . print_r($data, true));

// Проверка входных данных
if (isset($data['auth'])) {
    $authData = $data['auth'];
    $domain = $authData['domain'] ?? 'Домен не указан';
    $memberId = $authData['member_id'] ?? 'ID не указан';
    $authToken = $authData['access_token'] ?? 'Токен не указан';
    
    logMessage("Получены данные: Домен - $domain, Участник - $memberId");

    // Пример использования REST API с токеном
    $endpoint = "https://{$domain}/rest/some_endpoint/";
    $params = [
        'auth' => $authToken,
        // Добавьте параметры для запроса
    ];

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => $endpoint . '?' . http_build_query($params),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_SSL_VERIFYPEER => false,
    ]);

    $result = curl_exec($curl);
    curl_close($curl);

    logMessage("Результат REST API: " . $result);

    // Возврат успешного ответа и редирект на главную страницу
    header('Location: https://reklamaoko.ru');
    exit();
} else {
    // Обработка ошибок
    logMessage("Ошибка: Не переданы данные авторизации.");
    header('Content-Type: application/json');
    echo json_encode(['status' => 'error', 'message' => 'Не переданы данные авторизации.']);
    exit();
}
