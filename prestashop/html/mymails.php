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

// Decode a MIME part body using headers (Content-Transfer-Encoding, Content-Type charset)
function decode_part($body, $headers = []) {
    $body = (string)$body;
    // Determine Content-Transfer-Encoding
    $cte = '';
    if (!empty($headers['Content-Transfer-Encoding'])) {
        $cte = is_array($headers['Content-Transfer-Encoding']) ? implode(' ', $headers['Content-Transfer-Encoding']) : $headers['Content-Transfer-Encoding'];
    }
    $cte = strtolower($cte);
    if (strpos($cte, 'base64') !== false) {
        $decoded = @base64_decode($body, true);
        if ($decoded !== false) $body = $decoded;
    } elseif (strpos($cte, 'quoted-printable') !== false || strpos($cte, 'quoted_printable') !== false) {
        $body = @quoted_printable_decode($body);
    }

    // Detect charset from Content-Type header
    $charset = '';
    if (!empty($headers['Content-Type'])) {
        $ct = is_array($headers['Content-Type']) ? implode(' ', $headers['Content-Type']) : $headers['Content-Type'];
        if (preg_match('/charset\s*=\s*"?([^";\)\\\s]+)/i', $ct, $m)) {
            $charset = trim($m[1], "'\" ");
        }
    }

    // Normalize common charset names
    if ($charset) {
        $charset = strtolower($charset);
        if ($charset === 'us-ascii') $charset = 'ASCII';
    }

    // Convert to UTF-8 if needed
    if ($charset && strcasecmp($charset, 'utf-8') !== 0) {
        if (function_exists('mb_convert_encoding')) {
            $body = @mb_convert_encoding($body, 'UTF-8', $charset);
        } else {
            // Try iconv as fallback
            if (function_exists('iconv')) {
                $conv = @iconv($charset, 'UTF-8//TRANSLIT', $body);
                if ($conv !== false) $body = $conv;
            }
        }
    } else {
        // If charset unknown, try to detect and convert to UTF-8
        if (!mb_detect_encoding($body, 'UTF-8', true)) {
            $det = mb_detect_encoding($body, ['UTF-8', 'ISO-8859-2', 'WINDOWS-1250', 'CP1250', 'ASCII'], true);
            if ($det && strcasecmp($det, 'UTF-8') !== 0 && function_exists('mb_convert_encoding')) {
                $body = @mb_convert_encoding($body, 'UTF-8', $det);
            }
        }
    }

    return $body;
}

function find_plain_part($msg) {
    // 1) If MIME parts present
    if (!empty($msg['MIME']) && !empty($msg['MIME']['Parts']) && is_array($msg['MIME']['Parts'])) {
        foreach ($msg['MIME']['Parts'] as $part) {
            $h = [];
            if (!empty($part['Headers'])) $h = $part['Headers'];
            $ct = '';
            if (!empty($h['Content-Type'])) $ct = is_array($h['Content-Type']) ? implode(' ', $h['Content-Type']) : $h['Content-Type'];
            if (stripos($ct, 'plain') !== false && stripos($ct, 'html') === false) {
                $body = $part['Body'] ?? '';
                return decode_part($body, $part['Headers'] ?? []);
            }
        }
    }
    // 2) If Content->Body exists
    if (!empty($msg['Content']['Body'])) {
        $decoded = try_decode($msg['Content']['Body']);
        // if it's not HTML, return it
        if (!preg_match('/<\/?.{1,10}>/s', $decoded)) return $decoded;
    }
    // 3) If Raw->Data contains full MIME, try to extract the plain text part by boundary
    if (!empty($msg['Raw']['Data'])) {
        $raw = $msg['Raw']['Data'];
        if (preg_match('/Content-Type: multipart[\w\W]*?boundary="?([^"\s;]+)"?/i', $raw, $m)) {
            $boundary = preg_quote($m[1], '/');
                if (preg_match('/--' . $boundary . '[\s\S]*?Content-Type:[^\n]*plain[\s\S]*?\r?\n\r?\n([\s\S]*?)\r?\n--' . $boundary . '/', $raw, $m2)) {
                return try_decode($m2[1]);
            }
        }
        // fallback: try to find the first reasonably-sized text block (avoid binary blobs)
        if (preg_match('/\r?\n\r?\n([\s\S]{10,20000})\r?\n--/m', $raw, $m3)) {
            $candidate = try_decode($m3[1]);
            // reject if contains lots of HTML tags or base64 headers
            if (!preg_match('/<\/?(html|body|div|table|span|img)/i', $candidate) && !preg_match('/Content-Transfer-Encoding: base64/i', $raw)) {
                return $candidate;
            }
        }
    }
    return '';
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
                return decode_part($body, $part['Headers'] ?? []);
            }
        }
    }
    // 2) If Content->Body exists, try decode and check for HTML
    if (!empty($msg['Content']['Body'])) {
        $decoded = try_decode($msg['Content']['Body']);
        // If the decoded content contains MIME headers or boundary markers, try to extract only the HTML fragment
        if (preg_match('/Content-Type:|boundary=|=_[a-z0-9]{6,}/i', $decoded)) {
            // try to extract a full <html>...</html> block first
            if (preg_match('/(<(?:!doctype[\s\S]*?>)?[\s\S]*?<html[\s\S]*?<\/html>)/i', $decoded, $m)) {
                return $m[1];
            }
            // otherwise find the first HTML tag that looks like the start of the email body
            if (preg_match('/(<(?:body|div|table|p|h[1-6]|!doctype|html)[\s\S]*$)/i', $decoded, $m2)) {
                return $m2[1];
            }
            // as a last resort, strip leading headers up to the first '<' character
            $pos = strpos($decoded, '<');
            if ($pos !== false) return substr($decoded, $pos);
        }
        if (preg_match('/<\/?(html|body|div|p|table|h[1-6])/i', $decoded)) return $decoded;
    }
    // 3) If Raw->Data contains full MIME, try to extract the html part by a simple regex
    if (!empty($msg['Raw']['Data'])) {
        $raw = $msg['Raw']['Data'];
        // try to find boundary then HTML section
        if (preg_match('/Content-Type: multipart[\w\W]*?boundary="?([^"\s;]+)"?/i', $raw, $m)) {
            $boundary = preg_quote($m[1], '/');
            if (preg_match('/--' . $boundary . '[\s\S]*?Content-Type:[^\n]*html[\s\S]*?\r?\n\r?\n([\s\S]*?)\r?\n--' . $boundary . '/', $raw, $m2)) {
                // No headers available for this blob; try to detect encoding heuristically
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

// Build a map of Content-ID (without <> ) -> data URI for inline images
function build_cid_map($msg) {
    $map = [];
    // Check MIME parts for attachments
    if (!empty($msg['MIME']) && !empty($msg['MIME']['Parts']) && is_array($msg['MIME']['Parts'])) {
        foreach ($msg['MIME']['Parts'] as $part) {
            $headers = [];
            if (!empty($part['Headers'])) $headers = $part['Headers'];
            $ct = '';
            if (!empty($headers['Content-Type'])) $ct = is_array($headers['Content-Type']) ? implode(' ', $headers['Content-Type']) : $headers['Content-Type'];
            $dispo = '';
            if (!empty($headers['Content-Disposition'])) $dispo = is_array($headers['Content-Disposition']) ? implode(' ', $headers['Content-Disposition']) : $headers['Content-Disposition'];
            $cid = '';
            if (!empty($headers['Content-ID'])) $cid = is_array($headers['Content-ID']) ? $headers['Content-ID'][0] : $headers['Content-ID'];
            if ($cid) {
                // strip <> if present
                $cid = trim($cid);
                $cid = trim($cid, "<>\r\n \t");
            }
            $body = $part['Body'] ?? '';
            if ($cid && $body) {
                // guess mime type from Content-Type
                $mime = 'application/octet-stream';
                if (preg_match('/^\s*([^;\s]+)/', $ct, $m)) $mime = $m[1];
                // if Body looks already base64 or binary, assume base64 (MailHog parts often contain base64)
                $b64 = $body;
                // build data uri
                $data = 'data:' . $mime . ';base64,' . $b64;
                $map[$cid] = $data;
            }
        }
    }
    return $map;
}

function inline_cid_images($html, $map) {
    if (empty($map)) return $html;
    // Use a safer regex wrapped in a nowdoc to avoid PHP string-escaping issues.
    $pattern = <<<'PAT'
~<img\b[^>]*\bsrc\s*=\s*([\'\"])?cid:([^\'\">\s]+)\1[^>]*>~i
PAT;

    $html = preg_replace_callback($pattern, function($m) use ($map) {
        // $m[0] = whole <img ...> tag
        // $m[1] = optional quote character used (" or '), may be empty
        // $m[2] = the CID value (without the cid: prefix)
        $quote = $m[1] ?: '"';
        $cid = $m[2];
        $cid_clean = trim($cid, "<>\r\n \t");
        if (isset($map[$cid_clean])) {
            // Replace only the src attribute value in the original tag to preserve other attributes
            $orig = $m[0];
            // Build the search piece (src= + same quoting as original)
            $search = 'src=' . ($m[1] ?? '') . 'cid:' . $cid . ($m[1] ?? '');
            $replace = 'src=' . $quote . $map[$cid_clean] . $quote;
            return str_replace($search, $replace, $orig);
        }
        return $m[0];
    }, $html);

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
        // inline cid: images from attachments so they render in the iframe
        $cid_map = build_cid_map($msg);
        $doc = inline_cid_images($doc, $cid_map);
        $b64 = base64_encode($doc);
        echo '<iframe style="width:100%;min-height:600px;border:1px solid #ccc" src="data:text/html;base64,' . $b64 . '"></iframe>';
    } else {
        // fallback to plain text: try to extract a cleaned plain part instead of dumping full raw MIME
        $plain = find_plain_part($msg);
        if (empty($plain) && !empty($msg['Content']['Body'])) $plain = try_decode($msg['Content']['Body']);
        if (empty($plain) && !empty($msg['Raw']['Data'])) {
            // limit raw output and offer a toggle
            $raw = $msg['Raw']['Data'];
            $short = substr($raw, 0, 2000);
            $plain = try_decode($short) . "\n\n... (treść przycięta, kliknij 'Pokaż surowe')";
            $raw_full = htmlspecialchars($raw, ENT_QUOTES, 'UTF-8');
            echo '<pre style="display:none;" id="raw-' . md5($subject . $time) . '">' . $raw_full . '</pre>';
            echo '<p><a href="#" onclick="var e=document.getElementById(\'raw-' . md5($subject . $time) . '\'); if(e.style.display==\'none\'){e.style.display=\'block\'; this.textContent=\'Ukryj surowe\';}else{e.style.display=\'none\'; this.textContent=\'Pokaż surowe\';} return false;">Pokaż surowe</a></p>';
        }
        // limit long plain text to reasonable size
        if (strlen($plain) > 20000) $plain = substr($plain, 0, 20000) . "\n\n... (treść przycięta)";
        echo '<div class="plain-text">' . nl2br(safe($plain)) . '</div>';
    }
    echo '</div>';
    echo '</div>';
}

?>
</body>
</html>
