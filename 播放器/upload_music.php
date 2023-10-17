<?php
// 预设的密码
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

$expectedPassword = '1999xxy2038';

// 最大允许的文件大小（10MB）
$maxFileSize = 10 * 1024 * 1024;

// 接收上传的音频文件和密码
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['audio_file']) && isset($_POST['password'])) {
    $targetDirectory = './music/'; // 保存上传文件的目录

    // 确保目录存在
    if (!is_dir($targetDirectory)) {
        mkdir($targetDirectory, 0777, true);
    }

    // 验证密码
    $password = $_POST['password'];
    if ($password !== $expectedPassword) {
        // 密码不正确
        echo "密码错误。";
        exit;
    }

    // 验证文件大小
    $fileSize = $_FILES['audio_file']['size'];
    if ($fileSize > $maxFileSize) {
        // 文件大小超过限制
        echo "文件大小超过限制（最大允许10MB）。";
        exit;
    }

    // 生成唯一的文件名
    $fileName = $_FILES['audio_file']['name'];
    $targetPath = $targetDirectory . $fileName;

    // 移动上传文件到目标路径
    if (move_uploaded_file($_FILES['audio_file']['tmp_name'], $targetPath)) {
        // 文件移动成功
        echo "音频文件上传成功！";
    } else {
        // 文件移动失败
        echo "音频文件上传失败。";
    }
} else {
    // 请求方法不正确或未提供音频文件和密码
    echo "无效的请求。";
}
?>
