<?php

header('Access-Control-Allow-Origin: *'); 
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=utf-8'); 

// 数据库连接参数 
$host = 'localhost';
$user = 'dachui5014';  
$password = '1999xxy2038';
$database = 'dachui5014';

// 创建数据库连接
$mysqli = new mysqli($host, $user, $password, $database);
$mysqli->set_charset('utf8mb4');

// 检查连接是否成功
if ($mysqli->connect_errno) {
  die("连接失败: " . $mysqli->connect_error);
}

// 获取请求参数
$audio_id = isset($_GET['audio_id']) ? $_GET['audio_id'] : 'all';

// 构建SQL语句
if ($audio_id == 'all') {
  $sql = "SELECT * FROM JapaneseNewsAudio";  
} else {
  $sql = "SELECT * FROM JapaneseNewsAudio WHERE audio_id = ?";
}

// 准备语句
$stmt = $mysqli->prepare($sql);

// 绑定参数(如果不是查询所有)
if ($audio_id != 'all') {
  $stmt->bind_param("s", $audio_id); 
}

// 执行语句
$stmt->execute(); 

// 获取结果集
$result = $stmt->get_result();

// 转成数组
$rows = $result->fetch_all(MYSQLI_ASSOC);

// 输出JSON格式 
echo json_encode($rows,JSON_UNESCAPED_UNICODE);

// 关闭数据库链接
$mysqli->close();

?>