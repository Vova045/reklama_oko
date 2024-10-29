<?php
session_start();

$clientId = 'local.671fe1a5771b80.36776378';
$clientSecret = 'rxXLQH8AI2Ig9Uvgx7VmcsVKD39Qs46vIMiRGZiu2GsxHrAfE2';
$redirectUri = 'https://reklamaoko.ru/static/button_handler.php';

if (isset($_GET['code'])) {
    $authCode = $_GET['code'];

    $url = "https://oauth.bitrix.info/oauth/token";
    $postFields = [
        'grant_type' => 'authorization_code',
        'client_id' => $clientId,
        'client_secret' => $clientSecret,
        'redirect_uri' => $redirectUri,
        'code' => $authCode,
    ];

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($postFields));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/x-www-form-urlencoded'
    ]);

    $response = curl_exec($ch);

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

    curl_close($ch);
} else {
    $authUrl = "https://oauth.bitrix.info/oauth/authorize?client_id={$clientId}&redirect_uri={$redirectUri}&response_type=code";
    header("Location: $authUrl");
    exit();
}
?>
