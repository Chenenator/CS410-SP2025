<?php
/**
* @file weather_data.php
* @brief handles username, password, and tokens
*/
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");

// Config
$username = 'dennis.wong002@umb.edu';
$password = 123456;
$deviceId = '8b534c60-1667-11f0-8f83-43727cd6bc90';
$keys = 'TempF,TempC,Humidity,Brightness';
$tokenFile = __DIR__ . '/auth.json';

// Login function
/**
* @brief Handles login to ThingBoard and stores JWT token
* @param string $username The username email for ThingsBoard
* @param int $password The password for ThingsBoard
* @param string $tokenFile Path to the file where the token is 
* @return array Returns array with token
*/
function login($username, $password, $tokenFile) {
    $data = json_encode(['username' => $username, 'password' => $password]);
    $opts = ['http' => [
        'method'  => 'POST',
        'header'  => "Content-Type: application/json\r\n",
        'content' => $data
    ]];
    $context = stream_context_create($opts);
    $result = @file_get_contents('https://thingsboard.cloud/api/auth/login', false, $context);
    $auth = json_decode($result, true);
    if (isset($auth['token'])) {
        $auth['expires'] = time() + 3300;
        file_put_contents($tokenFile, json_encode($auth));
        return $auth;
    }
    return false;
}

// Refresh token
/**
* @brief Refresh the ThingsBoard JWT token
* @param string $refreshToken The refresh token
* @param string $tokenFile Path to the file where the token is
* @return array Returns array with new token
*/
function refreshToken($refreshToken, $tokenFile) {
    $opts = ['http' => [
        'method' => 'POST',
        'header' => "Content-Type: application/json\r\nAuthorization: Bearer $refreshToken\r\n"
    ]];
    $context = stream_context_create($opts);
    $result = @file_get_contents('https://thingsboard.cloud/api/auth/token', false, $context);
    $new = json_decode($result, true);
    if (isset($new['token'])) {
        $auth = json_decode(file_get_contents($tokenFile), true);
        $auth['token'] = $new['token'];
        $auth['expires'] = time() + 3300;
        file_put_contents($tokenFile, json_encode($auth));
        return $auth;
    }
    return false;
}

// Get current valid token
/**
* @brief Retrieves ThingsBoard JWT token
* @param string $username The username email for ThingsBoard
* @param int $password The ThingsBoard password
* @param string $tokenFile Path to the file where the token is
* @return array Returns array with auth
*/
function getToken($username, $password, $tokenFile) {
    if (!file_exists($tokenFile)) {
        return login($username, $password, $tokenFile);
    }
    $auth = json_decode(file_get_contents($tokenFile), true);
    if (time() < $auth['expires']) {
        return $auth;
    }
    return refreshToken($auth['refreshToken'], $tokenFile) ?: login($username, $password, $tokenFile);
}

// Try data fetch (with retry)
/**
* @brief Gets telemetry data from ThingsBoard
* @param array $auth Array containing JWT token
* @param string $deviceId The ID of the ThingsBoard
* @param string $keys list of telemetry columns
* @return string the JSON response 
*/
function fetchWeather($auth, $deviceId, $keys) {
    $url = "https://thingsboard.cloud/api/plugins/telemetry/DEVICE/$deviceId/values/timeseries?keys=$keys";
    $headers = [
        "http" => [
            "method" => "GET",
            "header" => "X-Authorization: Bearer {$auth['token']}\r\n"
        ]
    ];
    $context = stream_context_create($headers);
    $response = @file_get_contents($url, false, $context);
    return $response ? $response : false;
}

// Main logic
$auth = getToken($username, $password, $tokenFile);
$response = fetchWeather($auth, $deviceId, $keys);

// Retry if failed
if ($response === false) {
    $auth = login($username, $password, $tokenFile);
    $response = fetchWeather($auth, $deviceId, $keys);
}

if ($response === false) {
    http_response_code(500);
    echo json_encode(["error" => "Failed to retrieve weather data"]);
} else {
    echo $response;
}
?>
