<?php
// Чтение .env файла и установка переменных окружения
if (file_exists(__DIR__ . '/.env')) {
    $env = parse_ini_file(__DIR__ . '/.env');
    foreach ($env as $key => $value) {
        putenv("$key=$value");
    }
    error_log("Этап 1: .env файл прочитан и переменные окружения установлены");
}

// Настройки приложения
$clientId = getenv('CLIENT_ID');
$clientSecret = getenv('CLIENT_SECRET');
$redirectUri = getenv('REDIRECT_URI');
error_log("Этап 2: Настройки приложения загружены");

// Получение refresh_token из запроса
$refresh_token = $_POST['refresh_token'] ?? null;

if (!$refresh_token) {
    error_log("Этап 3: refresh_token не найден, пробуем использовать auth_code");
    
    // Если нет refresh_token, пробуем получить его через код авторизации
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    error_log("Этап 4: Данные из входящего запроса: " . json_encode($data));

    if (isset($data['auth_code'])) {
        $authCode = $data['auth_code'];
        error_log("Этап 5: Получен auth_code: $authCode");

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
        $curlError = curl_error($curl);
        curl_close($curl);

        if ($curlError) {
            error_log("Ошибка CURL при получении токена: $curlError");
        }

        $tokenData = json_decode($result, true);
        error_log("Этап 6: Ответ от сервера: " . json_encode($tokenData));

        if (isset($tokenData['access_token'])) {
            error_log("Этап 7: Токен доступа успешно получен");

            if (isset($tokenData['refresh_token'])) {
                error_log("Этап 8: Обновление токена с использованием refresh_token");

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
                $curlError = curl_error($curl);
                curl_close($curl);

                if ($curlError) {
                    error_log("Ошибка CURL при обновлении токена: $curlError");
                }

                $refreshTokenData = json_decode($refreshResult, true);
                error_log("Этап 9: Ответ от сервера при обновлении токена: " . json_encode($refreshTokenData));

                if (isset($refreshTokenData['access_token'])) {
                    error_log("Этап 10: Токены успешно обновлены");

                    echo json_encode([
                        'status' => 'success',
                        'message' => 'Токены обновлены и процесс завершен.',
                        'access_token' => $refreshTokenData['access_token'],
                        'refresh_token' => $refreshTokenData['refresh_token'],
                        'expires_in' => $refreshTokenData['expires_in'] ?? 3600,
                    ]);
                    exit();
                } else {
                    error_log("Ошибка обновления токенов: " . ($refreshTokenData['error_description'] ?? 'Неизвестная ошибка'));
                    echo json_encode([
                        'status' => 'error',
                        'message' => 'Ошибка обновления токенов: ' . ($refreshTokenData['error_description'] ?? 'Неизвестная ошибка'),
                    ]);
                    exit();
                }
            } else {
                error_log("Ошибка: Не получен refresh_token");
                echo json_encode([
                    'status' => 'error',
                    'message' => 'Не получен refresh_token.',
                ]);
                exit();
            }
        } else {
            error_log("Ошибка: Токен не получен");
            echo json_encode([
                'status' => 'error',
                'message' => 'Ошибка получения access_token.',
            ]);
            exit();
        }
    } else {
        error_log("Ошибка: Не передан auth_code");
        echo json_encode(['status' => 'error', 'message' => 'Не передан refresh_token и код авторизации']);
        exit();
    }
}
?>
