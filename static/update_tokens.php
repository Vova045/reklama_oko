<?php
// Подключение библиотеки для работы с .env
require __DIR__ . '/vendor/autoload.php'; // Путь к autoload, если используется Composer

// Загрузка переменных окружения
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

// Проверка наличия всех нужных переменных
$clientId = $_ENV['CLIENT_ID'] ?? null;
$clientSecret = $_ENV['CLIENT_SECRET'] ?? null;
$redirectUri = $_ENV['REDIRECT_URI_UPDATE'] ?? null;

// Если переменные окружения отсутствуют, выводим ошибку
if (!$clientId || !$clientSecret || !$redirectUri) {
    echo json_encode(['status' => 'error', 'message' => 'Недостающие переменные окружения']);
    exit();
}

// Получение refresh_token из запроса
$refresh_token = $_POST['refresh_token'] ?? null;

// Если refresh_token не передан, выводим ошибку
if (!$refresh_token) {
    echo json_encode(['status' => 'error', 'message' => 'Не передан refresh_token']);
    exit();
}

// Запрос на обновление токенов
$tokenUrl = 'https://oauth.bitrix.info/oauth/token/';
$params = [
    'grant_type' => 'refresh_token',
    'client_id' => $clientId,
    'client_secret' => $clientSecret,
    'refresh_token' => $refresh_token,
    'redirect_uri' => $redirectUri, // Добавляем redirect_uri
];

// Инициализация cURL
$curl = curl_init();
curl_setopt_array($curl, [
    CURLOPT_URL => $tokenUrl . '?' . http_build_query($params),
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_SSL_VERIFYPEER => false,
]);

$response = curl_exec($curl);
$curlError = curl_error($curl);
curl_close($curl);

// Если ошибка при запросе через cURL
if ($curlError) {
    echo json_encode(['status' => 'error', 'message' => "Ошибка cURL: " . htmlspecialchars($curlError)]);
    exit();
}

// Декодируем ответ от API
$data = json_decode($response, true);

// Если получен access_token, возвращаем успешный ответ
if (isset($data['access_token'])) {
    echo json_encode([
        'status' => 'success',
        'access_token' => $data['access_token'],
        'refresh_token' => $data['refresh_token'],
        'expires_in' => $data['expires_in'] ?? 3600,
    ]);
} else {
    // Если ошибка в ответе от API, выводим описание ошибки
    echo json_encode([
        'status' => 'error',
        'message' => $data['error_description'] ?? 'Неизвестная ошибка',
    ]);
}
?>
