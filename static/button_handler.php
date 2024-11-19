<?php
// Настройки приложения
$clientId = 'local.671fe1a5771b80.36776378';
$clientSecret = 'rxXLQH8AI2Ig9Uvgx7VmcsVKD39Qs46vIMiRGZiu2GsxHrAfE2';
$redirectUri = 'https://reklamaoko.ru/static/button_handler.php';

// Этап 1: Переадресация пользователя на страницу авторизации Bitrix24
if (!isset($_GET['code'])) {
    // Переадресация на страницу авторизации Bitrix
    $authUrl = "https://oauth.bitrix.info/oauth/authorize?client_id={$clientId}&redirect_uri={$redirectUri}&response_type=code";
    echo "<script>console.log('Этап 1: Переадресация на страницу авторизации Bitrix');</script>";
    header("Location: $authUrl");
    exit();
}

// Этап 2: Обработка редиректа после авторизации и получение code
if (isset($_GET['code'])) {
    $code = $_GET['code'];
    $domain = $_GET['domain'] ?? '';
    $state = $_GET['state'] ?? '';
    $redirectUrl = $_GET['redirect_url'] ?? '/';  // Получаем redirect_url для возвращения после авторизации

    echo "<script>console.log('Этап 2: Получен код авторизации');</script>";

    // Этап 3: Запрос токенов с использованием code
    echo "<script>console.log('Этап 3: Запрос токенов с использованием code');</script>";

    $tokenUrl = 'https://oauth.bitrix.info/oauth/token/';
    $params = [
        'grant_type' => 'authorization_code',
        'client_id' => $clientId,
        'client_secret' => $clientSecret,
        'redirect_uri' => $redirectUri,
        'code' => $code
    ];

    // Выполнение запроса cURL для получения токенов
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => $tokenUrl . '?' . http_build_query($params),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_SSL_VERIFYPEER => false,
    ]);

    $response = curl_exec($curl);
    curl_close($curl);

    $data = json_decode($response, true);

    if (isset($data['access_token'])) {
        $access_token = $data['access_token'];
        $refresh_token = $data['refresh_token'];
        echo "<script>console.log('Этап 3: Токен доступа получен');</script>";

        // Этап 4: Использование access_token для работы с REST API
        echo "<script>console.log('Этап 4: Использование токена для работы с REST API');</script>";

        $endpoint = "https://{your_domain}/rest/user.get.json";
        $params = [
            'auth' => $access_token,
            // Дополнительные параметры для REST-запроса
        ];

        // Выполнение REST-запроса
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => $endpoint . '?' . http_build_query($params),
            CURLOPT_RETURNTRANSFER => true,
        ]);

        $result = curl_exec($curl);
        curl_close($curl);

        echo "<script>console.log('Этап 4 завершен: Результат запроса - ' + " . json_encode($result) . ");</script>";
    } else {
        echo "<script>console.log('Ошибка авторизации: " . json_encode($data['error_description']) . "');</script>";
    }

    // Этап 5: Обновление токена с использованием refresh_token
    if (isset($refresh_token)) {
        echo "<script>console.log('Этап 5: Обновление токена с использованием refresh_token');</script>";

        $refreshUrl = 'https://oauth.bitrix.info/oauth/token/';
        $params = [
            'grant_type' => 'refresh_token',
            'client_id' => $clientId,
            'client_secret' => $clientSecret,
            'refresh_token' => $refresh_token,
        ];

        // Запрос обновленного токена cURL
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => $refreshUrl . '?' . http_build_query($params),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_SSL_VERIFYPEER => false,
        ]);

        $response = curl_exec($curl);
        curl_close($curl);

        $data = json_decode($response, true);

        if (isset($data['access_token'])) {
            $access_token = $data['access_token'];
            $refresh_token = $data['refresh_token'];
            echo "<script>console.log('Этап 5 завершен: Обновленный токен доступа получен');</script>";
        } else {
            echo "<script>console.log('Ошибка обновления токена: " . json_encode($data['error_description']) . "');</script>";
        }
    }
    
    // После успешной авторизации или обновления токена перенаправляем пользователя на исходную ссылку
    echo "<script>console.log('Перенаправление на исходную ссылку: " . $redirectUrl . "');</script>";
    header("Location: $redirectUrl");
    exit();
}
?>
