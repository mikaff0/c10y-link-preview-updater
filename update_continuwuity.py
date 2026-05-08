#!/usr/bin/env python3
import sqlite3
import os
import logging
import tomli
import tomli_w

# --- Logging Configuration (stdout/stderr only) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Log to stdout/stderr only (for Docker)
)
logger = logging.getLogger(__name__)

# --- Environment Variables ---
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "/data/c10y.toml")
DB_PATH = os.getenv("DB_PATH", "/data/morpheus link bot.db")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/data/continuwuity.toml")

def main():
    conn = None
    try:
        logger.info("Starting continuwuity link preview updater...")

        # --- 1. Read domains from DB ---
        logger.info(f"Connecting to database at: {DB_PATH}")
        try:
            # Use URI mode to handle paths with spaces
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro&immutable=1", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT domain FROM domain_rule WHERE is_blacklisted = FALSE")
            domains = [row[0] for row in cursor.fetchall()]
            logger.info(f"Found {len(domains)} domains in database.")
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

        # --- 2. Read TOML template ---
        logger.info(f"Reading TOML template from: {TEMPLATE_PATH}")
        try:
            with open(TEMPLATE_PATH, "rb") as f:
                template_data = tomli.load(f)
        except FileNotFoundError:
            logger.error(f"Template file not found: {TEMPLATE_PATH}")
            raise
        except tomli.TOMLDecodeError as e:
            logger.error(f"Invalid TOML in template: {e}")
            raise

        # --- 3. Update allowlist in [global] section ---
        logger.info("Updating url_preview_domain_explicit_allowlist in [global] section...")
        if "global" not in template_data:
            template_data["global"] = {}
        if "url_preview_domain_explicit_allowlist" not in template_data["global"]:
            logger.error("Key 'global.url_preview_domain_explicit_allowlist' not found in TOML template!")
            raise KeyError("global.url_preview_domain_explicit_allowlist missing")

        template_data["global"]["url_preview_domain_explicit_allowlist"] = domains

        # --- 4. Write new continuwuity.toml ---
        logger.info(f"Writing updated config to: {OUTPUT_PATH}")

        try:
            os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
            with open(OUTPUT_PATH, "wb") as f:
                tomli_w.dump(template_data, f)
        except PermissionError:
            logger.error(f"No write permission for {OUTPUT_PATH}")
            raise
        except Exception as e:
            logger.error(f"Failed to write {OUTPUT_PATH}: {e}")
            raise

        logger.info(f"FINISHED: {OUTPUT_PATH} updated with {len(domains)} domains!")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()