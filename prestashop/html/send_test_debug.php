<?php
require __DIR__ . '/config/config.inc.php';
require_once _PS_ROOT_DIR_ . '/init.php';

$idLang = (int) Configuration::get('PS_LANG_DEFAULT');
$template = 'contact';
$subject = 'Test contact';
$templateVars = ['{message}' => 'Debug test message'];
$to = Configuration::get('PS_SHOP_EMAIL');
$from = Configuration::get('PS_SHOP_EMAIL');
$fromName = Configuration::get('PS_SHOP_NAME');

// die=true to show errors
$result = Mail::send($idLang, $template, $subject, $templateVars, $to, null, $from, $fromName, null, null, _PS_MAIL_DIR_, true);
var_dump($result);
?>