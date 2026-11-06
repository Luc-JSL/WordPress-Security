<?php
/**
 * Hardening constants for wp-config.php.
 *
 * Paste these above the line that reads
 *   "That's all, stop editing! Happy publishing."
 * Regenerate the keys and salts with https://api.wordpress.org/secret-key/1.1/salt/
 * at onboarding and again after any incident.
 */

// Disable the theme and plugin file editors in the dashboard. An attacker with an
// admin login otherwise gets a PHP editor on the server for free.
define( 'DISALLOW_FILE_EDIT', true );

// Keep logins and the dashboard on HTTPS.
define( 'FORCE_SSL_ADMIN', true );

// Let WordPress apply minor core releases (security fixes) on its own. Major
// releases and plugins go through the monthly runbook.
define( 'WP_AUTO_UPDATE_CORE', 'minor' );

// Never show PHP errors to visitors; log them instead. Turn WP_DEBUG_LOG off
// again once you have read the log, or rotate it, so it cannot grow unbounded.
define( 'WP_DEBUG', false );
define( 'WP_DEBUG_DISPLAY', false );
@ini_set( 'display_errors', 0 );

// Limit stored post revisions so the database stays small enough to back up quickly.
define( 'WP_POST_REVISIONS', 10 );

// Optional: block plugin and theme installation entirely on sites where only you
// should be installing software. Also disables updates from the dashboard, so
// use it only where the monthly runbook runs from the command line.
// define( 'DISALLOW_FILE_MODS', true );
