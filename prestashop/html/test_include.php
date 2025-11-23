<?php
file_put_contents('/tmp/test_include.log','start\n', FILE_APPEND);
require __DIR__ . '/config/config.inc.php';
file_put_contents('/tmp/test_include.log','after require\n', FILE_APPEND);
