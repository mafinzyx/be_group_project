<?php
require __DIR__ . '/config/config.inc.php';
require_once _PS_ROOT_DIR_ . '/init.php';

$context = Context::getContext();
$shopId = (int)$context->shop->id;
$languages = Language::getLanguages(false);
$db = Db::getInstance();

function create_carrier_with_ranges($name, $ranges, $fee_label)
{
    global $languages, $db, $shopId;

    $carrier = new Carrier();
    $carrier->name = $name;
    $carrier->active = 1;
    $carrier->is_module = 0;
    $carrier->shipping_handling = 0;
    $carrier->shipping_external = 0;
    $carrier->external_module_name = '';
    $carrier->need_range = 1;
    $carrier->range_behavior = 0;
    $carrier->delay = [];
    foreach ($languages as $lang) {
        $carrier->delay[$lang['id_lang']] = $fee_label;
    }

    if (!$carrier->add()) {
        echo "Failed to add carrier $name\n";
        return false;
    }

    // associate carrier to current shop
    $db->execute('REPLACE INTO ' . _DB_PREFIX_ . 'carrier_shop (id_carrier, id_shop) VALUES ('.(int)$carrier->id.','. (int)$shopId .')');

    // assign carrier to all groups
    $groups = Group::getGroups(true);
    $groupIds = array();
    foreach ($groups as $g) $groupIds[] = (int)$g['id_group'];
    foreach ($groupIds as $gid) {
        $db->execute('REPLACE INTO ' . _DB_PREFIX_ . 'carrier_group (id_carrier, id_group) VALUES ('.(int)$carrier->id.','.$gid.')');
    }

    // assign carrier to all zones
    $zones = Zone::getZones(true);
    $zoneIds = array();
    foreach ($zones as $z) $zoneIds[] = (int)$z['id_zone'];
    foreach ($zoneIds as $zid) {
        $db->execute('REPLACE INTO ' . _DB_PREFIX_ . 'carrier_zone (id_carrier, id_zone) VALUES ('.(int)$carrier->id.','.$zid.')');
    }

    // insert ranges and delivery prices (price-based ranges)
    foreach ($ranges as $r) {
        $left = (float)$r['left'];
        $right = (float)$r['right'];
        $price = (float)$r['price'];
        $db->execute('INSERT INTO ' . _DB_PREFIX_ . 'range_price (id_carrier, delimiter1, delimiter2) VALUES ('.(int)$carrier->id.','.$left.','.$right.')');
        $id_range = (int)$db->Insert_ID();
        // add price for each shop
        $db->execute('INSERT INTO ' . _DB_PREFIX_ . 'delivery (id_range_price, id_carrier, id_shop, price) VALUES ('.$id_range.','.(int)$carrier->id.','. (int)$shopId .','.$price.')');
    }

    // add carrier language entries
    foreach ($languages as $lang) {
        $db->execute('REPLACE INTO ' . _DB_PREFIX_ . 'carrier_lang (id_carrier, id_lang, name, delay) VALUES ('.(int)$carrier->id.','.(int)$lang['id_lang'].',"'.pSQL($name).'","'.pSQL($fee_label).'")');
    }

    echo "Created carrier: $name (id=".$carrier->id.")\n";
    return $carrier->id;
}

// Carrier A: moderate fees, free shipping over 2000
$carrierA_ranges = [
    ['left' => 0, 'right' => 1999.99, 'price' => 150.00],
    ['left' => 2000.00, 'right' => 999999.00, 'price' => 0.00]
];

// Carrier B: cheaper for light orders, same free shipping threshold
$carrierB_ranges = [
    ['left' => 0, 'right' => 1999.99, 'price' => 90.00],
    ['left' => 2000.00, 'right' => 999999.00, 'price' => 0.00]
];

$idA = create_carrier_with_ranges('DobreWina Kurier A', $carrierA_ranges, 'Dostawa 1-3 dni');
$idB = create_carrier_with_ranges('DobreWina Kurier B', $carrierB_ranges, 'Dostawa 2-4 dni');

// Add weight limitation: block shipping for items heavier than 50kg by creating no valid weight range
// For simplicity we'll create weight ranges allowed up to 50000 (grams) and rely on product weight checks in front-end
// Alternatively, set a carrier range that doesn't cover >50kg; in PrestaShop weights are usually in kg depending on config.

echo "Done. Carriers created.\n";

?>