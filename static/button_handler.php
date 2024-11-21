<?php
// Функция для загрузки переменных из .env файла
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

// Функция для логирования
function logMessage($message) {
    file_put_contents(__DIR__ . '/log.txt', date('Y-m-d H:i:s') . " - $message" . PHP_EOL, FILE_APPEND);
}

// Логируем этапы выполнения
logMessage("Этап 2: Получен код авторизации");

// Получение кода авторизации
$input = file_get_contents('php://input');
$data = json_decode($input, true);

// Проверка наличия кода
if (isset($data['auth_code'])) {
    logMessage("Этап 3: Запрос токенов с использованием code");

    $authCode = $data['auth_code'];

    // Получение токена с использованием кода авторизации
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

    if (isset($tokenData['access_token'])) {
        logMessage("Этап 3: Токен доступа получен");

        // Если все прошло успешно, обновляем токен с использованием refresh_token
        if (isset($tokenData['refresh_token'])) {
            logMessage("Этап 5: Обновление токена с использованием refresh_token");

            $refreshParams = [
                'client_id' => $clientId,
                'client_secret' => $clientSecret,
                'refresh_token' => $tokenData['refresh_token'],
                'grant_type' => 'refresh_token',
                'redirect_uri' => $redirectUri,
            ];

            $curl = curl_init();
            curl_setopt_array($curl, [
                CURLOPT_URL => 'https://oauth.bitrix24.ru/oauth/token/' . '?' . http_build_query($refreshParams),
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_SSL_VERIFYPEER => false,
            ]);
            $refreshResult = curl_exec($curl);
            curl_close($curl);

            $refreshTokenData = json_decode($refreshResult, true);

            if (isset($refreshTokenData['access_token'])) {
                logMessage("Этап 5 завершен: Обновленный токен доступа получен");

                // Выводим успешный JSON ответ
                echo json_encode([
                    'status' => 'success',
                    'message' => 'Токены обновлены и процесс завершен.',
                    'access_token' => $refreshTokenData['access_token'],
                    'refresh_token' => $refreshTokenData['refresh_token'],
                    'expires_in' => $refreshTokenData['expires_in'] ?? 3600,
                ]);
                exit();
            } else {
                logMessage("Ошибка обновления токенов: " . ($refreshTokenData['error_description'] ?? 'Неизвестная ошибка'));
                echo json_encode([
                    'status' => 'error',
                    'message' => 'Ошибка обновления токенов: ' . ($refreshTokenData['error_description'] ?? 'Неизвестная ошибка'),
                ]);
                exit();
            }
        } else {
            logMessage("Ошибка: Не получен refresh_token");
            echo json_encode([
                'status' => 'error',
                'message' => 'Не получен refresh_token.',
            ]);
            exit();
        }
    } else {
        logMessage("Ошибка: Токен не получен");
        echo json_encode([
            'status' => 'error',
            'message' => 'Ошибка получения access_token.',
        ]);
        exit();
    }
} else {
    logMessage("Ошибка: Не передан код авторизации");
    echo json_encode([
        'status' => 'error',
        'message' => 'Не передан код авторизации.',
    ]);
    exit();
}
?>
