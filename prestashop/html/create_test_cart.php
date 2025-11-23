<?php
// Minimal SERVER variables for CLI runs
if (php_sapi_name() === 'cli') {
	if (!isset($_SERVER['REQUEST_METHOD'])) $_SERVER['REQUEST_METHOD'] = 'GET';
	if (!isset($_SERVER['HTTP_HOST'])) $_SERVER['HTTP_HOST'] = 'localhost';
	if (!isset($_SERVER['REMOTE_ADDR'])) $_SERVER['REMOTE_ADDR'] = '127.0.0.1';
}

require __DIR__ . '/config/config.inc.php';
require_once _PS_ROOT_DIR_ . '/init.php';
ini_set('display_errors',1); error_reporting(E_ALL);
file_put_contents('/tmp/create_test_cart.log', "Starting create_test_cart script\n", FILE_APPEND);

$cart = new Cart();
$cart->id_customer = 4;
$cart->id_currency = (int)Configuration::get('PS_CURRENCY_DEFAULT');
$cart->id_lang = (int)Configuration::get('PS_LANG_DEFAULT');
$cart->id_shop = (int)Context::getContext()->shop->id;
$cart->id_address_delivery = 8;
$cart->id_address_invoice = 8;
$addResult = $cart->add();
file_put_contents('/tmp/create_test_cart.log', "cart->add() returned: " . var_export($addResult, true) . "\n", FILE_APPEND);
file_put_contents('/tmp/create_test_cart.log', "Cart object id (after add): " . var_export($cart->id, true) . "\n", FILE_APPEND);
$success = $cart->updateQty(1, 1, null, false, 'up', 8, null, true);
file_put_contents('/tmp/create_test_cart.log', "updateQty returned: " . var_export($success, true) . "\n", FILE_APPEND);

file_put_contents('/tmp/create_test_cart.log', "Final cart id: " . $cart->id . "\n", FILE_APPEND);
