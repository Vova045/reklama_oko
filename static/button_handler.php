<?php
// Устанавливаем заголовок JSON для ответа
header('Content-Type: application/json');

// URL вашего Django-приложения
$appUrl = 'https://reklamaoko.ru';

// Получаем данные запроса
$request = file_get_contents('php://input');
$data = json_decode($request, true);

// Проверка на наличие access_token
$accessToken = $data['auth']['access_token'] ?? null;
if (!$accessToken) {
    echo json_encode(['status' => 'error', 'message' => 'Access token is missing']);
    exit;
}

// Функция для выполнения POST-запроса к Bitrix API
function sendRequest($method, $parameters, $accessToken) {
    $url = "https://your-bitrix24-url.com/rest/$method?auth=$accessToken";
    $options = [
        'http' => [
            'method'  => 'POST',
            'header'  => 'Content-type: application/json',
            'content' => json_encode($parameters)
        ]
    ];
    $context  = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    return json_decode($result, true);
}

// Настройка размещения приложения в левом меню
$leftMenuPlacement = [
    'scope' => 'crm',
    'placement' => 'left',
    'title' => 'Мое приложение',
    'handler' => $appUrl
];
sendRequest('placement.bind', $leftMenuPlacement, $accessToken);

// Настройка кнопки в списке сделок рядом с кнопкой «Создать»
$dealMenuPlacement = [
    'scope' => 'crm',
    'placement' => 'CRM_DEAL_LIST_MENU',
    'title' => 'Открыть приложение',
    'handler' => $appUrl
];
sendRequest('placement.bind', $dealMenuPlacement, $accessToken);

// Формируем ответ с URL приложения
$response = [
    'status' => 'success',
    'redirect_url' => $appUrl
];

// Возвращаем JSON-ответ
echo json_encode($response);
