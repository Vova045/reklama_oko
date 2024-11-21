<?php
// Чтение .env файла и установка переменных окружения
if (file_exists(__DIR__ . '/.env')) {
    $env = parse_ini_file(__DIR__ . '/.env');
    foreach ($env as $key => $value) {
        putenv("$key=$value");
    }
}

// Настройки приложения
$clientId = getenv('CLIENT_ID');
$clientSecret = getenv('CLIENT_SECRET');
$redirectUri = getenv('REDIRECT_URI_UPDATE');

// Получение refresh_token из запроса
$refresh_token = $_POST['refresh_token'] ?? null;

if (!$refresh_token) {
    // Если нет refresh_token, пробуем получить его через код авторизации
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    
    if (isset($data['auth_code'])) {
        // Получаем код авторизации
        $authCode = $data['auth_code'];

        // Получаем токены с использованием авторизационного кода
        $endpoint = 'https://oauth.bitrix24.ru/oauth/token/';
        $params = [
            'client_id' => $clientId,
            'client_secret' => $clientSecret,
            'code' => $authCode,
            'grant_type' => 'authorization_code',
            'redirect_uri' => $redirectUri,
        ];

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => $endpoint . '?' . http_build_query($params),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_SSL_VERIFYPEER => false,
        ]);
        $result = curl_exec($curl);
        curl_close($curl);

        $tokenData = json_decode($result, true);

        if (isset($tokenData['access_token']) && isset($tokenData['refresh_token'])) {
            // Сохраняем refresh_token
            $refresh_token = $tokenData['refresh_token'];
        } else {
            echo json_encode(['status' => 'error', 'message' => 'Ошибка получения токенов']);
            exit();
        }
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Не передан refresh_token и код авторизации']);
        exit();
    }
}

// Запрос на обновление токенов с использованием refresh_token
$tokenUrl = 'https://oauth.bitrix.info/oauth/token/';
$params = [
    'grant_type' => 'refresh_token',
    'client_id' => $clientId,
    'client_secret' => $clientSecret,
    'refresh_token' => $refresh_token,
    'redirect_uri' => $redirectUri, // Добавляем redirect_uri
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
