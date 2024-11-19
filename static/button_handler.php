<?php
// Настройки приложения
$clientId = 'local.671fe1a5771b80.36776378';
$clientSecret = 'rxXLQH8AI2Ig9Uvgx7VmcsVKD39Qs46vIMiRGZiu2GsxHrAfE2';
$redirectUri = 'https://reklamaoko.ru/static/button_handler.php';

// Функция для логирования
function logMessage($message) {
    file_put_contents('log.txt', date('Y-m-d H:i:s') . " - $message" . PHP_EOL, FILE_APPEND);
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
    // Этот запрос к API Bitrix24 для получения токенов
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

        // Токен получен, теперь используем его для работы с API (если нужно)
        logMessage("Этап 4: Использование токена для работы с REST API");

        // Пример запроса к REST API
        $endpoint = 'https://example.bitrix24.ru/rest/some_endpoint/';
        $params = [
            'auth' => $tokenData['access_token'],
        ];

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => $endpoint . '?' . http_build_query($params),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_SSL_VERIFYPEER => false,
        ]);
        $result = curl_exec($curl);
        curl_close($curl);

        logMessage("Этап 4 завершен: Результат запроса - " . $result);

        // Если все прошло успешно, обновляем токен с использованием refresh_token
        if (isset($tokenData['refresh_token'])) {
            logMessage("Этап 5: Обновление токена с использованием refresh_token");

            // Обновление токена с помощью refresh_token
            $refreshParams = [
                'client_id' => $clientId,
                'client_secret' => $clientSecret,
                'refresh_token' => $tokenData['refresh_token'],
                'grant_type' => 'refresh_token',
            ];

            $curl = curl_init();
            curl_setopt_array($curl, [
                CURLOPT_URL => $endpoint . '?' . http_build_query($refreshParams),
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_SSL_VERIFYPEER => false,
            ]);
            $refreshResult = curl_exec($curl);
            curl_close($curl);

            $refreshTokenData = json_decode($refreshResult, true);
            if (isset($refreshTokenData['access_token'])) {
                logMessage("Этап 5 завершен: Обновленный токен доступа получен");

                // Все этапы завершены успешно, редиректим на домен
                header('Location: https://reklamaoko.ru');
                exit();
            }
        }
    } else {
        logMessage("Ошибка: Токен не получен");
        // Если токен не получен, можно сделать редирект на страницу ошибки
        header('Location: https://reklamaoko.ru/error');
        exit();
    }
} else {
    logMessage("Ошибка: Не передан код авторизации");
    // Если нет кода авторизации, можно сделать редирект на страницу ошибки
    header('Location: https://reklamaoko.ru/error');
    exit();
}
?>
