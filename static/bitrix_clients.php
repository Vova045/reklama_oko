<?php
// Подключение .env для безопасности (если используется)
function loadEnv($filePath) {
    if (!file_exists($filePath)) {
        throw new Exception('.env file not found');
    }

    $lines = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos(trim($line), '#') === 0 || strpos($line, '=') === false) {
            continue; // Пропускаем комментарии и строки без '='
        }
        list($key, $value) = explode('=', $line, 2);
        $_ENV[trim($key)] = trim($value);
    }
}

try {
    loadEnv(__DIR__ . '/.env'); // Загружаем переменные окружения
} catch (Exception $e) {
    echo json_encode([
        'status' => 'error',
        'message' => 'Ошибка загрузки .env: ' . $e->getMessage(),
    ]);
    exit();
}

// Настройки для Битрикс24
$accessToken = $_ENV['ACCESS_TOKEN']; // Предполагается, что вы сохранили токен заранее
$bitrixEndpoint = 'https://oko.bitrix24.ru';

// Функция для получения клиентов
function getClients($accessToken, $endpoint) {
    $url = $endpoint . '/rest/crm.contact.list';

    $params = [
        'auth' => $accessToken,
        'select' => ['ID', 'NAME', 'LAST_NAME', 'EMAIL'], // Выбираем нужные поля
    ];

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => $url . '?' . http_build_query($params),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_SSL_VERIFYPEER => false,
    ]);
    $result = curl_exec($curl);
    curl_close($curl);

    return json_decode($result, true);
}

// Получаем клиентов
try {
    $clients = getClients($accessToken, $bitrixEndpoint);
    header('Content-Type: application/json');
    echo json_encode($clients);
} catch (Exception $e) {
    echo json_encode([
        'status' => 'error',
        'message' => 'Ошибка получения клиентов: ' . $e->getMessage(),
    ]);
}
