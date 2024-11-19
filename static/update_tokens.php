<?php
// Настройки приложения
$clientId = 'local.671fe1a5771b80.36776378';
$clientSecret = 'rxXLQH8AI2Ig9Uvgx7VmcsVKD39Qs46vIMiRGZiu2GsxHrAfE2';
$redirectUri = 'https://reklamaoko.ru/static/update_tokens.php';

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
