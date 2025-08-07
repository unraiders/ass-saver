#!/bin/sh
set -e

caddy start
exec reflex run --env prod --backend-only