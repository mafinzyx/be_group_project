<?php
require __DIR__ . '/config/config.inc.php';
require_once _PS_ROOT_DIR_ . '/init.php';

$shopEmail = Configuration::get('PS_SHOP_EMAIL');
$shopName = Configuration::get('PS_SHOP_NAME');
$langId = (int)Configuration::get('PS_LANG_DEFAULT');

$to = $shopEmail;
$subject = 'Test email from PrestaShop (automated)';
$templateVars = array('{message}' => 'This is a test email sent by an automated script to verify mail sending.');
$template = 'contact';
$from = $shopEmail;

// Try sending
$sent = Mail::Send(
    $langId,
    $template,
    $subject,
    $templateVars,
    $to,
    null,
    $from,
    $shopName,
    null,
    null,
    _PS_MAIL_DIR_,
    true,
    null
);

if ($sent) {
    echo "Mail send returned true\n";
} else {
    echo "Mail send returned false\n";
}

?>