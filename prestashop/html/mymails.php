<?php
// Simple MailHog viewer for logged-in customers
// Place this file in the PrestaShop root (`html/`) and open /mymails.php while logged in.

// Bootstrap PrestaShop environment
require __DIR__ . '/config/config.inc.php';
require_once _PS_ROOT_DIR_ . '/init.php';

use PrestaShop\PrestaShop\Core\Mail\MailGenerator;

@ini_set('display_errors', 1);
@error_reporting(E_ALL);

$context = Context::getContext();
$customer = $context->customer;

if (!Validate::isLoadedObject($customer) || !$customer->isLogged()) {
    header('HTTP/1.1 403 Forbidden');
    echo '<h2>Proszę się zalogować, aby zobaczyć swoje maile.</h2>';
    exit;
}

$email = $customer->email;

// Try a list of MailHog hosts (inside container 'mailhog' or host variants)
$hosts = [
    'http://mailhog:8025',
    'http://127.0.0.1:8025',
    'http://localhost:8025',
];

$result = null;
foreach ($hosts as $host) {
    // Use /api/v2/messages and filter client-side because /api/v2/search can return 400
    // for some query syntaxes in different MailHog builds/environments.
    $url = rtrim($host, '/') . '/api/v2/messages?limit=100';
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 2);
    curl_setopt($ch, CURLOPT_USERAGENT, 'PrestaShop-MailHog-Viewer/1.0');
    $resp = curl_exec($ch);
    $errno = curl_errno($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($errno === 0 && $http_code >= 200 && $http_code < 300 && $resp) {
        $result = @json_decode($resp, true);
        if ($result !== null) {
            // ensure consistent shape: MailHog returns {"items": [...] } or an array
            if (isset($result['items'])) {
                $all = $result['items'];
            } elseif (is_array($result)) {
                // sometimes API returns array of messages directly
                $all = $result;
            } else {
                $all = [];
            }
            // filter messages addressed to current customer
            $filtered = [];
            foreach ($all as $msg) {
                $headers = [];
                if (isset($msg['Content']) && isset($msg['Content']['Headers'])) {
                    $headers = $msg['Content']['Headers'];
                } elseif (isset($msg['Raw']) && isset($msg['Raw']['Headers'])) {
                    $headers = $msg['Raw']['Headers'];
                }
                $toList = [];
                if (!empty($headers['To']) && is_array($headers['To'])) {
                    $toList = $headers['To'];
                } elseif (!empty($headers['To'])) {
                    $toList = array($headers['To']);
                }
                // also check recipients field if present
                if (isset($msg['To']) && is_array($msg['To'])) {
                    foreach ($msg['To'] as $t) $toList[] = is_array($t) && isset($t['Mailbox']) ? ($t['Mailbox'].'@'.($t['Domain']??'')) : $t;
                }
                foreach ($toList as $t) {
                    if (stripos($t, $email) !== false) {
                        $filtered[] = $msg;
                        break;
                    }
                }
            }
            // store filtered result in the shape we expect
            $result = array('items' => $filtered);
            break;
        }
    }
}

function safe($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }

?><!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Moje maile - MailHog</title>
  <style>
    body{font-family:Arial,Helvetica,sans-serif;margin:20px}
    .mail{border:1px solid #ddd;padding:12px;margin-bottom:12px;border-radius:6px}
    .meta{color:#555;font-size:13px}
    .subject{font-weight:700;margin-bottom:6px}
    .body{margin-top:10px;border-top:1px dashed #eee;padding-top:8px}
    .empty{color:#777}
  </style>
</head>
<body>
  <h1>Moje maile (<?php echo safe($email); ?>)</h1>

<?php
if (!$result) {
    echo '<p class="empty">Nie udało się połączyć z MailHog. Upewnij się, że MailHog działa i jest dostępny pod portem 8025.</p>';
    echo '<p>Próbowałem hostów: ' . safe(implode(', ', $hosts)) . '</p>';
    echo '</body></html>';
    exit;
}

$items = [];
if (isset($result['items']) && is_array($result['items'])) {
    $items = $result['items'];
} elseif (isset($result['Messages']) && is_array($result['Messages'])) {
    $items = $result['Messages'];
} elseif (isset($result['total']) && isset($result['items']) && is_array($result['items'])) {
    $items = $result['items'];
}

if (empty($items)) {
    echo '<p class="empty">Brak wiadomości dla tego adresu.</p>';
    echo '</body></html>';
    exit;
}

// Define helper functions once (avoid redeclaration inside loop)
function try_decode($s) {
    if ($s === null) return '';
    $s = (string)$s;
    // Try quoted-printable decode
    $qp = @quoted_printable_decode($s);
    if ($qp && preg_match('/<\/?[a-z][\s\S]*>/i', $qp)) return $qp;
    // Try base64
    $b = @base64_decode($s, true);
    if ($b && preg_match('/<\/?[a-z][\s\S]*>/i', $b)) return $b;
    // Fall back to original
    return $s;
}

function find_html_part($msg) {
    // 1) If MIME parts present
    if (!empty($msg['MIME']) && !empty($msg['MIME']['Parts']) && is_array($msg['MIME']['Parts'])) {
        foreach ($msg['MIME']['Parts'] as $part) {
            $h = [];
            if (!empty($part['Headers'])) $h = $part['Headers'];
            $ct = '';
            if (!empty($h['Content-Type'])) $ct = is_array($h['Content-Type']) ? implode(' ', $h['Content-Type']) : $h['Content-Type'];
            if (stripos($ct, 'html') !== false) {
                $body = $part['Body'] ?? '';
                return try_decode($body);
            }
        }
    }
    // 2) If Content->Body exists, try decode and check for HTML
    if (!empty($msg['Content']['Body'])) {
        $decoded = try_decode($msg['Content']['Body']);
        if (preg_match('/<\/?(html|body|div|p|table|h[1-6])/i', $decoded)) return $decoded;
    }
    // 3) If Raw->Data contains full MIME, try to extract the html part by a simple regex
    if (!empty($msg['Raw']['Data'])) {
        $raw = $msg['Raw']['Data'];
        // try to find boundary then HTML section
        if (preg_match('/Content-Type: multipart[\w\W]*?boundary="?([^"\s;]+)"?/i', $raw, $m)) {
            $boundary = preg_quote($m[1], '/');
            if (preg_match('/--' . $boundary . '[\s\S]*?Content-Type:[^\n]*html[\s\S]*?\r?\n\r?\n([\s\S]*?)\r?\n--' . $boundary . '/', $raw, $m2)) {
                return try_decode($m2[1]);
            }
        }
        // fallback: try to find first HTML tag block
        if (preg_match('/(<html[\s\S]*<\/html>)/i', $raw, $m3)) return try_decode($m3[1]);
    }
    // 4) No HTML found — return empty
    return '';
}

function sanitize_mail_html($html) {
    $html = (string)$html;
    // remove script tags
    $html = preg_replace('#<script[^>]*?>.*?</script>#is', '', $html);
    // remove on* attributes (onclick, onmouseover etc.)
    $html = preg_replace('#\s+on[a-zA-Z]+\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)#i', '', $html);
    // remove javascript: in href/src
    $html = preg_replace('#(href|src)\s*=\s*("|\')?\s*javascript:[^"\'>\s]+("|\')?#i', '$1="#"', $html);
    return $html;
}

// Display items
foreach ($items as $msg) {
    // MailHog structure: Headers often in $msg['Content']['Headers']
    $headers = [];
    if (isset($msg['Content']) && isset($msg['Content']['Headers'])) {
        $headers = $msg['Content']['Headers'];
    } elseif (isset($msg['Raw']) && isset($msg['Raw']['Headers'])) {
        $headers = $msg['Raw']['Headers'];
    }

    $subject = '';
    if (!empty($headers['Subject']) && is_array($headers['Subject'])) $subject = $headers['Subject'][0];
    if (empty($subject) && isset($msg['Content']['Subject'])) $subject = $msg['Content']['Subject'];

    $from = '';
    if (!empty($headers['From']) && is_array($headers['From'])) $from = $headers['From'][0];
    $to = '';
    if (!empty($headers['To']) && is_array($headers['To'])) $to = implode(', ', $headers['To']);

    $time = '';
    if (isset($msg['Created'])) $time = $msg['Created'];
    if (empty($time) && isset($msg['Raw']) && isset($msg['Raw']['Time'])) $time = $msg['Raw']['Time'];

    $htmlBody = find_html_part($msg);

    echo '<div class="mail">';
    echo '<div class="subject">' . safe($subject) . '</div>';
    echo '<div class="meta">Od: ' . safe($from) . ' | Do: ' . safe($to) . ' | ' . safe($time) . '</div>';
    echo '<div class="body">';
    if (!empty($htmlBody)) {
        // Render HTML inside an iframe to avoid theme CSS interfering with email HTML
        $doc = sanitize_mail_html($htmlBody);
        $b64 = base64_encode($doc);
        echo '<iframe style="width:100%;min-height:600px;border:1px solid #ccc" src="data:text/html;base64,' . $b64 . '"></iframe>';
    } else {
        // fallback to plain text
        $plain = '';
        if (!empty($msg['Content']['Body'])) $plain = $msg['Content']['Body'];
        elseif (!empty($msg['Raw']['Data'])) $plain = $msg['Raw']['Data'];
        echo nl2br(safe(try_decode($plain)));
    }
    echo '</div>';
    echo '</div>';
}

?>
</body>
</html>
