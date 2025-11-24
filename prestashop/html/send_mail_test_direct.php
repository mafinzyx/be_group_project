<?php
require __DIR__ . '/config/config.inc.php';
require_once _PS_ROOT_DIR_ . '/init.php';

$smtpChecked = true;
$smtpServer = Configuration::get('PS_MAIL_SERVER');
$content = 'Test content from send_mail_test_direct';
$subject = 'Test subject';
$type = null;
$to = Configuration::get('PS_SHOP_EMAIL');
$from = Configuration::get('PS_SHOP_EMAIL');
$smtpLogin = Configuration::get('PS_MAIL_USER');
$smtpPassword = Configuration::get('PS_MAIL_PASSWD');
$smtpPort = Configuration::get('PS_MAIL_SMTP_PORT');
 $smtpEncryption = Configuration::get('PS_MAIL_SMTP_ENCRYPTION');

$r = Mail::sendMailTest(
    $smtpChecked,
    $smtpServer,
    $content,
    $subject,
    $type,
    $to,
    $from,
    $smtpLogin,
    $smtpPassword,
    $smtpPort,
    $smtpEncryption
);
var_dump($r);
?>