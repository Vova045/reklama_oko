<?php
// Установите ваши параметры
$clientId = 'rxXLQH8AI2Ig9Uvgx7VmcsVKD39Qs46vIMiRGZiu2GsxHrAfE2';
$clientSecret = '671fe1a5771b80.36776378';
$redirectUri = 'https://reklamaoko.ru/static/button_handler.php'; // URL для редиректа

// Получаем код из параметров URL
$code = $_GET['code'] ?? null;

if ($code) {
    // Получаем токен
    $tokenUrl = "https://oauth.bitrix.info/oauth/token";
    $data = [
        'grant_type' => 'authorization_code',
        'client_id' => $clientId,
        'client_secret' => $clientSecret,
        'redirect_uri' => $redirectUri,
        'code' => $code
    ];

    // Инициализация cURL
    $ch = curl_init($tokenUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));

    // Выполняем запрос
    $response = curl_exec($ch);
    curl_close($ch);

    // Декодируем ответ
    $tokenData = json_decode($response, true);

    // Проверяем на наличие ошибок
    if (isset($tokenData['error'])) {
        echo "Ошибка: " . $tokenData['error_description'];
    } else {
        // Токен успешно получен
        $accessToken = $tokenData['access_token'];
        echo "Access Token: " . htmlspecialchars($accessToken);
        
        // Здесь можно сохранить токен или выполнить другие действия
    }
} else {
    echo "Код авторизации отсутствует.";
}
?>
