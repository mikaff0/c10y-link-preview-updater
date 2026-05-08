# Continuwuity Link Preview Updater

**Automatically update your [Continuwuity Matrix Homeserver](https://continuwuity.org) URL preview allowlist with domains from your [Morpheus Link Bot](https://github.com/M2tecDev/morpheus-link-bot) instance.**

This Docker container periodically reads domains from your Morpheus Link Bot's database and updates the `url_preview_domain_explicit_allowlist` in your Continuwuity configuration file (`continuwuity.toml`). This allows you to dynamically manage which domains are allowed for URL previews in your Matrix server.

---

## Requirements

- **Docker** and **Docker Compose** installed.
- **Read access** to the Morpheus Link Bot database file (`<maubot-data-directory>/dbs/morpheus link bot.db`)
- **Read access** to a Continuwuity configuration template file (`c10y.toml`).
- **Write access** to your Continuwuity server's `continuwuity.toml` file.

---

## Setup

### 1. Prepare the Template File (`c10y.toml`)

Your template file should be a copy of your current `continuwuity.toml` with the following adjustments:

- Ensure the `[global]` section exists.
- Add the `url_preview_domain_explicit_allowlist` key under `[global]` if it does not already exist. For example:

```toml
[global]
# Your existing Continuwuity configuration
url_preview_domain_explicit_allowlist = []
```

> **Note:** Any domains already present in `url_preview_domain_explicit_allowlist` will be **replaced** with the domains from your Morpheus Link Bot database.

---

### 2. Configure and run [`compose.yaml`](compose.yaml)

Use the following [`compose.yaml`](compose.yaml) file to start the container. **Adjust the paths and environment variables to match your setup.**

```yaml
services:
  continuwuity-link-preview-updater:
    image: mikaff0/c10y-link-preview-updater:latest # ghcr.io/mikaff0/c10y-link-preview-updater:latest
    container_name: continuwuity-updater
    environment:
      - CRON_SCHEDULE=0 * * * *  # hourly o'clock
      # - TZ=Europe/Berlin         # Set your timezone (default: UTC)
      # Optional: Customize paths (default values shown below)
      # - TEMPLATE_PATH=/data/c10y.toml
      # - DB_PATH=/data/morpheus link bot.db
      # - OUTPUT_PATH=/data/continuwuity.toml
    volumes:
      - /path/to/maubot/dbs/morpheus link bot.db:/data/morpheus link bot.db:ro
      - /path/to/your/c10y.toml:/data/c10y.toml:ro
      - /path/to/your/continuwuity.toml:/data/continuwuity.toml:rw
    restart: unless-stopped
```

---

## How It Works

1. **Database Access**: The script connects to the Morpheus Link Bot's SQLite database in **read-only mode** and retrieves all non-blacklisted domains.
2. **TOML Parsing**: It reads your `c10y.toml` template file and updates the `url_preview_domain_explicit_allowlist` under the `[global]` section with the domains from the database.
3. **Output**: The updated configuration is written to your `continuwuity.toml` file.
4. **Scheduling**: The script runs on a schedule defined by the `CRON_SCHEDULE` environment variable.

---

### Debugging Steps

1. **Check container logs:**
  ```bash
   docker logs c10y-link-preview-updater
  ```
2. **Verify volume mounts:**
  ```bash
   docker exec -it c10y-link-preview-updater ls -la /data/
  ```
3. **Test database access manually:**
  ```bash
   docker exec -it c10y-link-preview-updater sqlite3 "file:/data/morpheus link bot.db?mode=ro&immutable=1" "SELECT domain FROM domain_rule WHERE is_blacklisted = FALSE;"
  ```

---

## Future Updates

- **Preserve Existing Domains**: Merge domains from the template file with those from the database, instead of replacing them entirely.
- **Config Reload**: Automatically reload the Continuwuity configuration after updates (requires Continuwuity API support).

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL)** – see the [LICENSE](LICENSE) file for details.