<?php
// Настройки приложения
$clientId = 'local.671fe1a5771b80.36776378';
$clientSecret = 'rxXLQH8AI2Ig9Uvgx7VmcsVKD39Qs46vIMiRGZiu2GsxHrAfE2';
$redirectUri = 'https://reklamaoko.ru/static/button_handler.php';

// Буферизация вывода для предотвращения ошибок с header()
ob_start();

// Этап 1: Переадресация пользователя на страницу авторизации Bitrix24
if (!isset($_GET['code'])) {
    $authUrl = "https://oauth.bitrix.info/oauth/authorize?client_id={$clientId}&redirect_uri={$redirectUri}&response_type=code";
    header("Location: $authUrl");
    exit();
}

// Этап 2: Обработка редиректа после авторизации и получение токенов
if (isset($_GET['code'])) {
    $code = $_GET['code'];

    // Запрос токенов с использованием кода авторизации
    $tokenUrl = 'https://oauth.bitrix.info/oauth/token/';
    $params = [
        'grant_type' => 'authorization_code',
        'client_id' => $clientId,
        'client_secret' => $clientSecret,
        'redirect_uri' => $redirectUri,
        'code' => $code,
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
        die("Ошибка cURL: " . htmlspecialchars($curlError));
    }

    $data = json_decode($response, true);

    if (isset($data['access_token'])) {
        // Успешно получили токены
        $access_token = $data['access_token'];
        $refresh_token = $data['refresh_token'];
        $expires_in = $data['expires_in'] ?? 3600; // Время жизни access_token в секундах
        $domain = $_GET['domain'] ?? 'unknown'; // Получите домен, если он передается
        $member_id = $_GET['member_id'] ?? 'unknown'; // Получите member_id, если он передается

        // Логируем токены
        echo "Авторизация успешна! Access token: " . htmlspecialchars($access_token) . "<br>";
        echo "Refresh token: " . htmlspecialchars($refresh_token);

        // Формируем данные для отправки в Django
        $postData = [
            'DOMAIN' => $domain,
            'AUTH_ID' => $access_token,
            'REFRESH_ID' => $refresh_token,
            'member_id' => $member_id,
            'AUTH_EXPIRES' => $expires_in,
        ];

        // Отправка данных в Django
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, "https://reklamaoko.ru/install/");
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($postData));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

        $response = curl_exec($ch);
        $curlError = curl_error($ch);
        curl_close($ch);

        if ($curlError) {
            die("Ошибка при отправке данных в Django: " . htmlspecialchars($curlError));
        }

        // Логируем ответ от Django
        echo "Ответ от Django: " . htmlspecialchars($response);
    } else {
        // Ошибка при получении токенов
        echo "Ошибка авторизации: " . htmlspecialchars($data['error_description'] ?? 'Неизвестная ошибка');
    }
    
    // Очищаем буфер и завершаем
    ob_end_flush();
    exit();
}
?>
