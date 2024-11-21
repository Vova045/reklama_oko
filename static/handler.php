<?php
// URL для перенаправления
$redirectUrl = 'https://reklamaoko.ru/calculation_list';

// Логирование для отладки
$logFile = __DIR__ . '/handler_log.txt';
file_put_contents($logFile, date('Y-m-d H:i:s') . " - Запрос на handler.php\n", FILE_APPEND);

// Заголовки для перенаправления
header("Location: $redirectUrl");
exit();
