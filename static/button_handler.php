<?php
// Устанавливаем заголовок JSON для ответа
header('Content-Type: application/json');

// Получаем данные запроса
$request = file_get_contents('php://input');
$data = json_decode($request, true);

// Логируем входящие данные для отладки
error_log("Получен запрос: " . print_r($data, true));

// Проверка на наличие access_token
$accessToken = $data['auth']['access_token'] ?? null;

if (!$accessToken) {
    // Логируем ошибку, если токен отсутствует
    error_log("Ошибка: Access token отсутствует.");
    echo json_encode(['status' => 'error', 'message' => 'Access token is missing']);
    exit;
}

// Логируем, что токен получен
error_log("Access token получен: " . $accessToken);

// Пример для проверки добавленных размещений
$placements = [
    "left_menu", 
    "crm.deal.list.menu", 
    "crm.company.details", 
    "crm.contact.details",
    "crm.activity.list.menu",
    "task.list.menu",
    "user.profile.menu"
];

// Ответ, чтобы отобразить в консоли браузера, что обработчик работает
$response = [
    'status' => 'success',
    'message' => 'Handler is running',
    'access_token' => $accessToken,
    'added_placements' => []
];

// Перебираем массив и добавляем каждый плейсмент
foreach ($placements as $placement) {
    // Проверяем наличие каждого плейсмента, добавленного ранее (пример)
    // Здесь должен быть код API для проверки добавленных плейсментов (в реальности потребуется запрос к Bitrix24 для проверки)
    $isAdded = true; // Здесь установим true для примера
    
    if ($isAdded) {
        $response['added_placements'][] = $placement;
        error_log("Placement добавлен: " . $placement);
    } else {
        error_log("Ошибка добавления placement: " . $placement);
    }
}

// Логируем результат для отладки
error_log("Результат выполнения: " . print_r($response, true));

// Возвращаем JSON-ответ
echo json_encode($response);
?>
