<?php
$host = 'mailhog';
$port = 1025;
$from = 'no-reply@localhost';
$to = 'prestashop@prestashop.com';
$subject = 'Raw SMTP test';
$body = "This is a raw SMTP test message from PHP.\n";

$fp = fsockopen($host, $port, $errno, $errstr, 5);
if (!$fp) {
    echo "Socket open failed: $errstr ($errno)\n";
    exit(1);
}

function get_resp($fp) {
    $resp = '';
    while ($line = fgets($fp, 515)) {
        $resp .= $line;
        if (substr($line, 3, 1) == ' ') break;
    }
    return $resp;
}

echo "Connected, server says:\n" . get_resp($fp) . "\n";

fputs($fp, "EHLO localhost\r\n");
echo "EHLO -> " . get_resp($fp) . "\n";

fputs($fp, "MAIL FROM: <$from>\r\n");
echo "MAIL FROM -> " . get_resp($fp) . "\n";

fputs($fp, "RCPT TO: <$to>\r\n");
echo "RCPT TO -> " . get_resp($fp) . "\n";

fputs($fp, "DATA\r\n");
echo "DATA -> " . get_resp($fp) . "\n";

$headers = "From: $from\r\n";
$headers .= "To: $to\r\n";
$headers .= "Subject: $subject\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

fputs($fp, $headers . "\r\n" . $body . "\r\n.\r\n");
echo "After DATA -> " . get_resp($fp) . "\n";

fputs($fp, "QUIT\r\n");
echo "QUIT -> " . get_resp($fp) . "\n";

fclose($fp);

echo "Done.\n";
?>