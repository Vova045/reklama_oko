<?php
// Проверьте, был ли передан код авторизации
if (isset($_GET['code'])) {
    $authCode = $_GET['code'];
    echo "Код авторизации: " . htmlspecialchars($authCode) . "<br>";
} else {
    echo "Код авторизации не получен.<br>";
}

// Пример получения токена (замените значения на свои)
$clientId = 'rxXLQH8AI2Ig9Uvgx7VmcsVKD39Qs46vIMiRGZiu2GsxHrAfE2';
$clientSecret = 'local.671fe1a5771b80.36776378';
$redirectUri = 'https://reklamaoko.ru/static/button_handler.php';

// Получение токена
if (isset($authCode)) {
    $url = "https://oauth.bitrix.info/oauth/token";
    $postFields = [
        'grant_type' => 'authorization_code',
        'client_id' => $clientId,
        'client_secret' => $clientSecret,
        'redirect_uri' => $redirectUri,
        'code' => $authCode,
    ];

    // Инициализация cURL
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($postFields));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    // Выполнение запроса
    $response = curl_exec($ch);

    // Обработка ответа
    if ($response === false) {
        echo 'Ошибка cURL: ' . curl_error($ch);
    } else {
        $responseData = json_decode($response, true);
        if (isset($responseData['access_token'])) {
            echo "Access Token: " . htmlspecialchars($responseData['access_token']);
        } else {
            echo "Ошибка получения Access Token: " . htmlspecialchars($response);
        }
    }

    // Закрытие cURL
    curl_close($ch);
}
?>
