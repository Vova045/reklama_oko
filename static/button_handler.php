<?php
// Устанавливаем заголовок JSON для ответа
header('Content-Type: application/json');

// Получаем данные запроса
$request = file_get_contents('php://input');
$data = json_decode($request, true);

// Логируем входящие данные для отладки
error_log(print_r($data, true)); // Это поможет увидеть, что приходит в запросе

// Проверка на наличие access_token
$accessToken = $data['auth']['access_token'] ?? null;

if (!$accessToken) {
    echo json_encode(['status' => 'error', 'message' => 'Access token is missing']);
    exit;
}

// Если токен получен, отправляем ответ
$response = [
    'status' => 'success',
    'message' => 'Access token received',
    'access_token' => $accessToken // Выводим токен для проверки (не рекомендуется в продакшене)
];

// Возвращаем JSON-ответ
echo json_encode($response);
