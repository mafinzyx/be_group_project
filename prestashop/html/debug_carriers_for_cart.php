<?php
// Ensure minimal SERVER variables for CLI execution
if (php_sapi_name() === 'cli') {
    if (!isset($_SERVER['REQUEST_METHOD'])) $_SERVER['REQUEST_METHOD'] = 'GET';
    if (!isset($_SERVER['HTTP_HOST'])) $_SERVER['HTTP_HOST'] = 'localhost';
    if (!isset($_SERVER['REMOTE_ADDR'])) $_SERVER['REMOTE_ADDR'] = '127.0.0.1';
}

ini_set('display_errors', 1);
error_reporting(E_ALL);
file_put_contents('/tmp/debug_carriers_for_cart.log', "Starting debug script\n", FILE_APPEND);

require __DIR__ . '/config/config.inc.php';
require_once _PS_ROOT_DIR_ . '/init.php';
file_put_contents('/tmp/debug_carriers_for_cart.log', "After init\n", FILE_APPEND);

if (php_sapi_name() === 'cli') {
    if ($argc < 2) {
        echo "Usage: php debug_carriers_for_cart.php <cart_id>\n";
        exit(1);
    }
    $cartId = (int)$argv[1];
} else {
    $cartId = isset($_GET['cart_id']) ? (int)$_GET['cart_id'] : 0;
}

if (!$cartId) {
    echo "Missing cart id\n";
    exit(1);
}

$cart = new Cart($cartId);
if (!Validate::isLoadedObject($cart)) {
    echo "Cart $cartId not found\n";
    exit(1);
}

$context = Context::getContext();
$context->cart = $cart;
if ($cart->id_customer) $context->customer = new Customer($cart->id_customer);
if ($cart->id_address_delivery) $context->address = new Address($cart->id_address_delivery);

echo "Cart id: {$cart->id}\n";
echo "Customer id: {$cart->id_customer}\n";
echo "Address delivery id: {$cart->id_address_delivery}\n";
echo "Cart total products: " . $cart->getOrderTotal(false, Cart::ONLY_PRODUCTS) . "\n";
echo "Cart weight: " . $cart->getTotalWeight() . "\n";

$langId = $context->language->id;

echo "\nPackage list:\n";
$packages = $cart->getPackageList(true);
print_r($packages);

echo "\nDelivery option list:\n";
$deliveryOptions = $cart->getDeliveryOptionList($langId);
print_r($deliveryOptions);

echo "\nCarrier zones mapping (for carriers 5 & 6):\n";
$db = Db::getInstance();
$rows = $db->executeS('SELECT id_carrier,id_zone FROM '._DB_PREFIX_."carrier_zone WHERE id_carrier IN (5,6)");
print_r($rows);

echo "\nCarrier price/weight ranges and delivery table rows:\n";
$rows = $db->executeS('SELECT d.id_delivery,d.id_range_price,d.id_range_weight,d.id_carrier,d.price, rp.delimiter1 AS price_from, rp.delimiter2 AS price_to, rw.delimiter1 AS weight_from, rw.delimiter2 AS weight_to FROM '._DB_PREFIX_."delivery d LEFT JOIN "._DB_PREFIX_."range_price rp ON d.id_range_price=rp.id_range_price LEFT JOIN "._DB_PREFIX_."range_weight rw ON d.id_range_weight=rw.id_range_weight WHERE d.id_carrier IN (5,6) ORDER BY d.id_delivery");
print_r($rows);

echo "\nDone.\n";
