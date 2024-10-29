<?php
header('Content-Type: application/json');

// Получение данных запроса
$request = file_get_contents('php://input');
$data = json_decode($request, true);

// Получаем access_token
$accessToken = $data['auth']['access_token'] ?? null;
if (!$accessToken) {
    echo json_encode(['status' => 'error', 'message' => 'Access token is missing']);
    exit;
}

// URL Bitrix24 для добавления размещений
$addUrl = "https://oko.bitrix24.ru/rest/placement.bind";

// Список размещений для добавления
$placements = [
    ['PLACEMENT' => 'left_menu', 'TITLE' => 'Калькуляция', 'HANDLER' => 'https://reklamaoko.ru'],
    ['PLACEMENT' => 'crm.deal.list.menu', 'TITLE' => 'Калькуляция', 'HANDLER' => 'https://reklamaoko.ru'],
    ['PLACEMENT' => 'crm.company.details', 'TITLE' => 'Калькуляция', 'HANDLER' => 'https://reklamaoko.ru'],
    ['PLACEMENT' => 'crm.contact.details', 'TITLE' => 'Калькуляция', 'HANDLER' => 'https://reklamaoko.ru'],
    ['PLACEMENT' => 'crm.activity.list.menu', 'TITLE' => 'Калькуляция', 'HANDLER' => 'https://reklamaoko.ru'],
    ['PLACEMENT' => 'task.list.menu', 'TITLE' => 'Калькуляция', 'HANDLER' => 'https://reklamaoko.ru'],
    ['PLACEMENT' => 'user.profile.menu', 'TITLE' => 'Калькуляция', 'HANDLER' => 'https://reklamaoko.ru']
];

// Функция для добавления размещений
function addPlacement($placement, $accessToken, $addUrl) {
    $payload = json_encode($placement);
    $opts = [
        'http' => [
            'method' => 'POST',
            'header' => "Authorization: Bearer $accessToken\r\n" .
                        "Content-Type: application/json\r\n",
            'content' => $payload
        ]
    ];
    $context = stream_context_create($opts);
    $result = file_get_contents($addUrl, false, $context);
    return json_decode($result, true);
}

// Добавление каждого размещения и сбор результатов
$results = [];
foreach ($placements as $placement) {
    $result = addPlacement($placement, $accessToken, $addUrl);
    $results[] = [
        'placement' => $placement['PLACEMENT'],
        'status' => $result['error'] ?? 'Added successfully'
    ];
}

// Возвращаем результат на страницу
echo json_encode(['status' => 'complete', 'results' => $results]);
?>
