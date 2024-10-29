<?php
session_start(); // Начинаем сессии, если это необходимо

// Убедитесь, что код авторизации присутствует
if (isset($_GET['code'])) {
    $authCode = $_GET['code'];

    // Пример получения токена
    $clientId = 'local.671fe1a5771b80.36776378';
    $clientSecret = 'rxXLQH8AI2Ig9Uvgx7VmcsVKD39Qs46vIMiRGZiu2GsxHrAfE2';
    $redirectUri = 'https://reklamaoko.ru/static/button_handler.php';

    // Получение токена
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
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/x-www-form-urlencoded'
    ]);

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
} else {
    // Если код авторизации отсутствует, перенаправляем на страницу авторизации
    $clientId = 'local.671fe1a5771b80.36776378';
    $redirectUri = 'https://reklamaoko.ru/static/button_handler.php';

    $authUrl = "https://oauth.bitrix.info/oauth/authorize?client_id=local.671fe1a5771b80.36776378&redirect_uri=https://reklamaoko.ru/static/button_handler.php&response_type=code ";
    header("Location: $authUrl");
    exit();
}
?>
