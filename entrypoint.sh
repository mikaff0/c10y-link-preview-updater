#!/bin/sh

# Create crontab
echo "=== Update cron job ==="
echo "$CRON_SCHEDULE echo '=== Running script (cron) ===' && python3 /app/update_continuwuity.py" > /etc/crontabs/root

# Run cron and the script at container startup
echo "=== Running script and cron (startup) ==="
python3 /app/update_continuwuity.py
exec crond -f