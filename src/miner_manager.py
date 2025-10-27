import os
import subprocess
import time
import signal
import logging
from threading import Thread
from dataclasses import dataclass

SUPPORTED_COINS = {
    "RVN": {
        "algo": "kawpow",
        "default_pool": "stratum+tcp://rvn.2miners.com:6060",
        "miner": "nbminer",  # open-source alternative: lolMiner
        "args": lambda wallet, worker, pool: [
            "-a", "kawpow",
            "-o", pool,
            "-u", f"{wallet}.{worker}",
        ],
        "stats_url": lambda wallet: f"https://rvn.2miners.com/api/accounts/{wallet}",
    },
    "ETC": {
        "algo": "ethash",
        "default_pool": "stratum+tcp://etc.2miners.com:1010",
        "miner": "lolMiner",
        "args": lambda wallet, worker, pool: [
            "--algo", "ETHASH",
            "--pool", pool,
            "--user", f"{wallet}.{worker}",
        ],
        "stats_url": lambda wallet: f"https://etc.2miners.com/api/accounts/{wallet}",
    },
    "ZEC": {
        "algo": "equihash",
        "default_pool": "stratum+tcp://zec.2miners.com:1010",
        "miner": "miniZ",
        "args": lambda wallet, worker, pool: [
            "--url", pool,
            "--user", f"{wallet}.{worker}",
        ],
        "stats_url": lambda wallet: f"https://zec.2miners.com/api/accounts/{wallet}",
    },
}

@dataclass
class MinerConfig:
    wallet: str
    pool: str
    coin: str
    worker: str = "worker01"
    log_level: str = "INFO"
    restart_backoff: int = 10

class MinerManager:
    def __init__(self, cfg: MinerConfig):
        self.cfg = cfg
        self.proc = None
        self.stop_flag = False
        logging.basicConfig(level=getattr(logging, cfg.log_level.upper(), logging.INFO),
                            format='%(asctime)s %(levelname)s %(message)s')

    def _get_cmd(self):
        coin = self.cfg.coin.upper()
        if coin not in SUPPORTED_COINS:
            raise ValueError(f"Unsupported coin: {coin}")
        meta = SUPPORTED_COINS[coin]
        pool = self.cfg.pool or meta["default_pool"]
        wallet = self.cfg.wallet
        worker = self.cfg.worker

        miner = meta["miner"]
        args = meta["args"](wallet, worker, pool)

        # Resolve miner binary path from environment or PATH
        miner_bin = os.environ.get("MINER_BIN", miner)
        return [miner_bin] + args

    def start(self):
        cmd = self._get_cmd()
        logging.info(f"Starting miner: {' '.join(cmd)}")
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        Thread(target=self._log_stream, daemon=True).start()

    def _log_stream(self):
        if not self.proc or not self.proc.stdout:
            return
        for line in self.proc.stdout:
            if self.stop_flag:
                break
            self._parse_and_log(line.strip())

    def _parse_and_log(self, line: str):
        # Very lightweight parsing of common miner outputs
        if any(k in line.lower() for k in ["accepted", "share found", "new job"]):
            logging.info(f"EARNING_EVENT: {line}")
        elif "error" in line.lower() or "fail" in line.lower():
            logging.warning(f"MINER_WARN: {line}")
        else:
            logging.debug(line)

    def stop(self):
        self.stop_flag = True
        if self.proc and self.proc.poll() is None:
            logging.info("Stopping miner process...")
            self.proc.send_signal(signal.SIGTERM)
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logging.info("Force killing miner...")
                self.proc.kill()

    def run_forever(self):
        while not self.stop_flag:
            try:
                self.start()
                while self.proc and self.proc.poll() is None and not self.stop_flag:
                    time.sleep(2)
                if self.stop_flag:
                    break
                logging.warning("Miner exited unexpectedly. Restarting...")
                time.sleep(self.cfg.restart_backoff)
            except Exception as e:
                logging.exception(f"Miner crashed: {e}. Restarting in {self.cfg.restart_backoff}s...")
                time.sleep(self.cfg.restart_backoff)


def from_env() -> MinerConfig:
    coin = os.getenv("COIN", "RVN").upper()
    meta = SUPPORTED_COINS.get(coin, SUPPORTED_COINS["RVN"])
    return MinerConfig(
        wallet=os.getenv("WALLET_ADDRESS", ""),
        pool=os.getenv("POOL_URL", meta["default_pool"]),
        coin=coin,
        worker=os.getenv("WORKER_NAME", "worker01"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        restart_backoff=int(os.getenv("RESTART_BACKOFF", "10")),
    )


if __name__ == "__main__":
    cfg = from_env()
    if not cfg.wallet:
        raise SystemExit("WALLET_ADDRESS is required. Set it in .env or env vars.")
    mm = MinerManager(cfg)
    try:
        mm.run_forever()
    except KeyboardInterrupt:
        mm.stop()
        logging.info("Miner stopped by user.")
