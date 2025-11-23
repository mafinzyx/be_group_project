<?php
// CLI-safe minimal server variables
if (php_sapi_name() === 'cli') {
    if (!isset($_SERVER['REQUEST_METHOD'])) $_SERVER['REQUEST_METHOD'] = 'GET';
    if (!isset($_SERVER['HTTP_HOST'])) $_SERVER['HTTP_HOST'] = 'localhost';
    if (!isset($_SERVER['REMOTE_ADDR'])) $_SERVER['REMOTE_ADDR'] = '127.0.0.1';
}
ini_set('display_errors',1); error_reporting(E_ALL);
// Early marker to show the script started before includes
file_put_contents('/tmp/run_delivery_test.preinit', date('c') . " - preinit\n", FILE_APPEND);

require __DIR__ . '/config/config.inc.php';
require_once _PS_ROOT_DIR_ . '/init.php';

// Marker so we can tell the script started after init
file_put_contents('/tmp/run_delivery_test.started', date('c') . " - started\n", FILE_APPEND);

// Use product 1 and address id 8 (Poland)
$prodId = 1;
$addrId = 8;
$customerId = 4;

$cart = new Cart();
$cart->id_customer = $customerId;
$cart->id_currency = (int)Configuration::get('PS_CURRENCY_DEFAULT');
$cart->id_lang = (int)Configuration::get('PS_LANG_DEFAULT');
$cart->id_shop = (int)Context::getContext()->shop->id;
$cart->id_address_delivery = $addrId;
$cart->id_address_invoice = $addrId;
$cart->add();

file_put_contents('/tmp/run_delivery_test.log', "Created cart id: " . $cart->id . "\n", FILE_APPEND);
echo "Created cart id: " . $cart->id . "\n";

// Add product
$res = $cart->updateQty(1, $prodId, null, false, 'up', $addrId);
file_put_contents('/tmp/run_delivery_test.log', "updateQty result: " . var_export($res, true) . "\n", FILE_APPEND);
var_export($res);
echo "\n";

$context = Context::getContext();
$context->cart = $cart;
$context->customer = new Customer($customerId);
if ($addrId) $context->address = new Address($addrId);

$langId = $context->language->id;

echo "Cart total products: " . $cart->getOrderTotal(false, Cart::ONLY_PRODUCTS) . "\n";
echo "Cart weight: " . $cart->getTotalWeight() . "\n";

echo "Package list:\n";
$packages = $cart->getPackageList(true);
file_put_contents('/tmp/run_delivery_test.log', "Cart total products: " . $cart->getOrderTotal(false, Cart::ONLY_PRODUCTS) . "\n", FILE_APPEND);
file_put_contents('/tmp/run_delivery_test.log', "Cart weight: " . $cart->getTotalWeight() . "\n", FILE_APPEND);
file_put_contents('/tmp/run_delivery_test.log', "Package list:\n" . print_r($packages, true) . "\n", FILE_APPEND);
print_r($packages);

echo "Delivery option list:\n";
$deliveryOptions = $cart->getDeliveryOptionList($langId);
file_put_contents('/tmp/run_delivery_test.log', "Delivery option list:\n" . print_r($deliveryOptions, true) . "\n", FILE_APPEND);
print_r($deliveryOptions);
