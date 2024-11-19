<?php
// Функция для загрузки переменных из .env файла
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

// Загружаем переменные из .env
try {
    loadEnv(__DIR__ . '/.env');
} catch (Exception $e) {
    echo json_encode([
        'status' => 'error',
        'message' => 'Ошибка загрузки .env: ' . $e->getMessage(),
    ]);
    exit();
}

// Настройки приложения
$clientId = $_ENV['CLIENT_ID'];
$clientSecret = $_ENV['CLIENT_SECRET'];
$redirectUri = $_ENV['REDIRECT_URI'];

// Получение refresh_token из запроса
$refresh_token = $_POST['refresh_token'] ?? null;

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
    'redirect_uri' => $redirectUri,
];

$curl = curl_init();
curl_setopt_array($curl, [
    CURLOPT_URL => $tokenUrl . '?' . http_build_query($params),
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_SSL_VERIFYPEER => false,
]);

$response = curl_exec($curl);
$curlError = curl_error($curl);
curl_close($curl);

if ($curlError) {
    echo json_encode(['status' => 'error', 'message' => "Ошибка cURL: " . htmlspecialchars($curlError)]);
    exit();
}

$data = json_decode($response, true);

if (isset($data['access_token'])) {
    echo json_encode([
        'status' => 'success',
        'access_token' => $data['access_token'],
        'refresh_token' => $data['refresh_token'],
        'expires_in' => $data['expires_in'] ?? 3600,
    ]);
} else {
    echo json_encode([
        'status' => 'error',
        'message' => $data['error_description'] ?? 'Неизвестная ошибка',
    ]);
}
?>
