<?php
require __DIR__ . '/config/config.inc.php';
require_once _PS_ROOT_DIR_ . '/init.php';

$db = Db::getInstance();

// Find carriers by name
$carriers = $db->executeS("SELECT id_carrier, name FROM "._DB_PREFIX_."carrier WHERE name LIKE 'DobreWina%'");
if (empty($carriers)) {
    echo "No DobreWina carriers found. Run create_carriers_and_configure.php first.\n";
    exit(0);
}

foreach ($carriers as $c) {
    $id = (int)$c['id_carrier'];
    echo "Processing carrier id=$id name={$c['name']}\n";

    // Check if weight ranges exist for this carrier
    $exists = $db->getValue('SELECT COUNT(*) FROM '._DB_PREFIX_."range_weight WHERE id_carrier=".$id);
    if ($exists > 0) {
        echo "  Weight ranges already exist, skipping.\n";
        continue;
    }

    // Insert a single allowed weight range 0 - 50 (kg)
    // Note: PrestaShop stores weights with delimiter1/delimiter2 in the same unit as product weight config.
    $left = 0;
    $right = 50;
    $db->execute('INSERT INTO '._DB_PREFIX_."range_weight (id_carrier, delimiter1, delimiter2) VALUES (".$id.",".$left.",".$right.")");
    $id_range = (int)$db->Insert_ID();

    // Create delivery price for this weight range for the current shop
    $shopId = (int)Context::getContext()->shop->id;
    // Set price for weight-based delivery — use same price as price-based fallback (approx). We'll set 0 to avoid interfering; actual availability is main goal.
    $price = 0.00;
    $db->execute('INSERT INTO '._DB_PREFIX_."delivery (id_range_weight, id_carrier, id_shop, price) VALUES (".$id_range.",".$id.",".$shopId.",".$price.")");

    echo "  Added weight range 0-50 for carrier id=$id (range id=$id_range).\n";
}

echo "Done. Weight ranges added (allowed up to 50kg). If order weight >50kg, carriers will be unavailable.\n";

?>
