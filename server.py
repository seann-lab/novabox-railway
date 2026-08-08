"""Railway Server Entrypoint & Logger for Novabox.

Provides non-interactive automated execution with web-friendly standard logging.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

from config import Config
from exporter import export_all
from models import WORKING_MODELS, test_all
from providers.blackbox import AccountResult, BlackboxClient
from providers.tempmail import generate_email, wait_for_otp
from main import load_state, save_state, append_key, done_emails

# Set up logging to stdout for Railway logs dashboard
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("novabox-railway")


async def run_farm(count: int, workers: int, domain: str, headless: bool):
    cfg = Config(max_workers=workers, headless=headless, tempmail_domain=domain)
    state = load_state(cfg.output_dir)
    already = done_emails(state)

    logger.info(f"🚀 Starting Novabox Farm | Target: {count} | Workers: {workers} | Domain: {domain}")
    logger.info(f"📊 Previous completed accounts: {len(already)}")

    remaining = max(0, count - len(already))
    if remaining == 0:
        logger.info(f"✅ All {count} requested accounts are already created!")
        return

    sem = asyncio.Semaphore(cfg.max_workers)
    launched = 0
    tasks = []

    async def _account_worker(wid: int, email: str, password: str):
        async with sem:
            logger.info(f"[Worker {wid}] Starting registration for {email}...")
            result = AccountResult(email=email, password=password)
            start_time = time.monotonic()
            client = None
            try:
                client = BlackboxClient(cfg)
                await client.start()
                api_key = await client.register_and_create_key(email, password)
                
                result.api_key = api_key
                result.success = True
                result.elapsed = time.monotonic() - start_time
                logger.info(f"[Worker {wid}] SUCCESS! Created key for {email} ({result.elapsed:.1f}s)")
            except Exception as e:
                result.success = False
                result.error = str(e)
                result.elapsed = time.monotonic() - start_time
                logger.error(f"[Worker {wid}] FAILED for {email}: {e}")
            finally:
                if client:
                    try:
                        await client.stop()
                    except Exception:
                        pass

            # Save state atomically
            record = {
                "email": result.email,
                "password": result.password,
                "api_key": result.api_key,
                "success": result.success,
                "error": result.error,
                "elapsed": result.elapsed,
            }
            state.setdefault("accounts", []).append(record)
            save_state(cfg.output_dir, state)
            if result.success:
                append_key(cfg.output_dir, record)

    while launched < remaining:
        email = generate_email(cfg.tempmail_domain)
        while email in already:
            email = generate_email(cfg.tempmail_domain)
        
        password = generate_email(cfg.tempmail_domain).split("@")[0] + "Pass123!"
        tasks.append(asyncio.create_task(_account_worker(launched % cfg.max_workers, email, password)))
        launched += 1

    await asyncio.gather(*tasks)
    
    # Summary & Auto Export
    state_updated = load_state(cfg.output_dir)
    accounts = state_updated.get("accounts", [])
    succeeded = [a for a in accounts if a.get("success")]
    logger.info(f"✨ Finished! Total Succeeded: {len(succeeded)} / {len(accounts)}")
    
    # Auto-export outputs
    export_all(cfg.output_dir)
    logger.info(f"📁 Output files saved to '{cfg.output_dir}/'")


def main():
    parser = argparse.ArgumentParser(description="Novabox Railway Non-Interactive Server")
    parser.add_argument("--count", type=int, default=10, help="Total accounts to register")
    parser.add_argument("--workers", type=int, default=3, help="Concurrent workers")
    parser.add_argument("--domain", type=str, default="catchmail.io", help="Tempmail domain")
    parser.add_argument("--headless", action="store_true", default=True, help="Headless mode")
    args = parser.parse_args()

    try:
        asyncio.run(run_farm(args.count, args.workers, args.domain, args.headless))
    except KeyboardInterrupt:
        logger.info("Stopped by user.")


if __name__ == "__main__":
    main()
