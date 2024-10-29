<?php
// Устанавливаем заголовок JSON для ответа
header('Content-Type: application/json');

// Получаем данные запроса
$request = file_get_contents('php://input');
$data = json_decode($request, true);

// Проверка на наличие access_token
$accessToken = $data['access_token'] ?? null;

if (!$accessToken) {
    echo json_encode(['status' => 'error', 'message' => 'Access token is missing']);
    exit;
}

// Логируем токен для отладки
error_log("Access Token: " . $accessToken); // Убедитесь, что это только в режиме разработки

// Ответ для проверки
$response = [
    'status' => 'success',
    'message' => 'Access token received and processed',
    'access_token' => $accessToken
];

echo json_encode($response);
