<?php
// Настройки приложения
$clientId = 'local.671fe1a5771b80.36776378';
$clientSecret = 'rxXLQH8AI2Ig9Uvgx7VmcsVKD39Qs46vIMiRGZiu2GsxHrAfE2';
$redirectUri = 'https://reklamaoko.ru/static/button_handler.php';

// Функция для логирования
function logMessage($message) {
    file_put_contents('log.txt', date('Y-m-d H:i:s') . " - $message" . PHP_EOL, FILE_APPEND);
}

// Этап 1: Переадресация на авторизацию, если нет кода
if (!isset($_GET['code'])) {
    $authUrl = "https://oauth.bitrix.info/oauth/authorize?client_id={$clientId}&redirect_uri={$redirectUri}&response_type=code";
    header("Location: $authUrl");
    exit();
}

// Этап 2: Получение и обработка `code`
if (isset($_GET['code'])) {
    $code = $_GET['code'];
    $domain = $_GET['domain'] ?? '';
    $state = $_GET['state'] ?? '';

    if (empty($domain)) {
        logMessage("Ошибка: параметр domain отсутствует.");
        die("Ошибка: домен не указан.");
    }

    // Этап 3: Запрос токенов с использованием code
    $tokenUrl = 'https://oauth.bitrix.info/oauth/token/';
    $params = [
        'grant_type' => 'authorization_code',
        'client_id' => $clientId,
        'client_secret' => $clientSecret,
        'redirect_uri' => $redirectUri,
        'code' => $code
    ];

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => $tokenUrl . '?' . http_build_query($params),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_SSL_VERIFYPEER => false,
    ]);

    $response = curl_exec($curl);
    curl_close($curl);

    $data = json_decode($response, true);

    if (isset($data['access_token'])) {
        $accessToken = $data['access_token'];
        $refreshToken = $data['refresh_token'];

        logMessage("Этап 3: Токен доступа получен. Access Token: {$accessToken}");

        // Этап 4: Пример использования REST API
        $endpoint = "https://{$domain}/rest/some_endpoint/";
        $apiParams = [
            'auth' => $accessToken,
            // Здесь добавьте дополнительные параметры для запроса
        ];

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => $endpoint . '?' . http_build_query($apiParams),
            CURLOPT_RETURNTRANSFER => true,
        ]);

        $result = curl_exec($curl);
        curl_close($curl);

        $resultData = json_decode($result, true);

        if (isset($resultData['error'])) {
            logMessage("Ошибка REST API: " . $resultData['error_description']);
            echo "Ошибка REST API: " . htmlspecialchars($resultData['error_description']);
        } else {
            logMessage("Успешный REST API запрос: " . print_r($resultData, true));
            echo "Результат запроса: " . print_r($resultData, true);
        }
    } else {
        logMessage("Ошибка получения токенов: " . json_encode($data));
        echo "Ошибка: " . htmlspecialchars($data['error_description']);
    }

    // Этап 5: Обновление токенов с использованием refresh_token
    if (!empty($refreshToken)) {
        $refreshUrl = 'https://oauth.bitrix.info/oauth/token/';
        $refreshParams = [
            'grant_type' => 'refresh_token',
            'client_id' => $clientId,
            'client_secret' => $clientSecret,
            'refresh_token' => $refreshToken,
        ];

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => $refreshUrl . '?' . http_build_query($refreshParams),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_SSL_VERIFYPEER => false,
        ]);

        $refreshResponse = curl_exec($curl);
        curl_close($curl);

        $refreshData = json_decode($refreshResponse, true);

        if (isset($refreshData['access_token'])) {
            logMessage("Обновленный токен получен. Access Token: " . $refreshData['access_token']);
        } else {
            logMessage("Ошибка обновления токенов: " . json_encode($refreshData));
            echo "Ошибка обновления токенов: " . htmlspecialchars($refreshData['error_description']);
        }
    } else {
        logMessage("Отсутствует refresh_token, обновление невозможно.");
    }
}
