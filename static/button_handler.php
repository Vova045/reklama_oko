<?php
// Включаем отображение ошибок и логирование
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Устанавливаем заголовок JSON для ответа
header('Content-Type: application/json');

// Логируем начало выполнения обработчика
error_log("Handler.php начат");

// Получаем данные запроса
$request = file_get_contents('php://input');
$data = json_decode($request, true);

// Логируем входящие данные для отладки
error_log("Полученные данные: " . print_r($data, true));

// Проверка на наличие access_token
$accessToken = $data['auth']['access_token'] ?? null;

if (!$accessToken) {
    error_log("Access token отсутствует.");
    echo json_encode(['status' => 'error', 'message' => 'Access token is missing']);
    exit;
}

// Логируем полученный токен
error_log("Получен access token: " . $accessToken);

// Если токен получен, отправляем ответ
$response = [
    'status' => 'success',
    'message' => 'Access token received',
    'access_token' => $accessToken // Выводим токен для проверки (не рекомендуется в продакшене)
];

// Логируем успешное завершение обработки
error_log("Ответ подготовлен: " . print_r($response, true));

// Возвращаем JSON-ответ
echo json_encode($response);
?>
