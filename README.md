# GPU Mining Automation

Automate GPU mining on CUDA-capable cards with setup, monitoring, and profitability assessment. This project demonstrates why Bitcoin SHA-256 mining on GPUs is not economical in 2025 while providing tooling to benchmark GPUs, mine alternative GPU-friendly coins, and calculate profitability with electricity costs.

## Key Features
- Setup scripts and Dockerized environment for reproducible runs
- GPU detection, benchmarking (hashrate, power), and monitoring
- Profitability calculator with electricity cost, pool fees, and coin difficulty
- Templates for miners (e.g., kawpow, ethash, equihash) via external miners
- Alerting hooks and run logs

## Important Note on Bitcoin with GPUs
Bitcoin (SHA-256) mining is dominated by ASICs; GPUs are orders of magnitude slower and less power-efficient. Use these tools primarily to mine GPU-friendly, ASIC-resistant coins (e.g., Ravencoin/KAWPOW, ETC/Ethash, ZEC/Equihash) and optionally convert to BTC.

References:
- Bitcoin mining calculator: https://www.coinwarz.com/mining/bitcoin/calculator
- GPU-friendly coin overview: https://www.miners1688.com/which-cryptocurrencies-are-best-for-gpu-mining-in-2025/

## Repository Structure
```
.
├─ docker/
│  ├─ Dockerfile
│  └─ entrypoint.sh
├─ src/
│  ├─ main.py
│  ├─ miner_manager.py
│  ├─ profitability.py
│  ├─ gpu_utils.py
│  └─ config.py
├─ scripts/
│  ├─ setup.sh
│  └─ quick_start.sh
├─ .env.example
├─ .gitignore
└─ README.md
```

## Quick Start
1) Prerequisites
- NVIDIA GPU with recent CUDA drivers
- Docker + NVIDIA Container Toolkit (or Python 3.10+ with nvml/nvidia-smi)
- Mining pool credentials for your target coin

2) Clone and configure
```
git clone https://github.com/<your-username>/gpu-mining-automation.git
cd gpu-mining-automation
cp .env.example .env
# Edit .env values (wallet address, pool URL, power cost, etc.)
```

3) Run with Docker
```
docker build -t gpu-mining-automation -f docker/Dockerfile .
docker run --gpus all --env-file .env --rm gpu-mining-automation
```

Or run locally
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Configuration (.env)
- WALLET_ADDRESS=<your_wallet>
- POOL_URL=stratum+tcp://<host>:<port>
- COIN=RVN|ETC|ZEC
- POWER_COST_USD_PER_KWH=0.05
- TARGET_ALGO=KAWPOW|ETHASH|EQUIHASH
- LOG_LEVEL=INFO

## Profitability Calculations
The calculator estimates daily profit:
- Revenue/day = hashrate × network_factor(coin, algo, difficulty, block_reward, price)
- Cost/day = power_watts × 24/1000 × power_cost
- Profit/day = Revenue/day − Cost/day − Pool fees

Example (illustrative):
- RTX 3060 Ti @ KAWPOW ~ 26 MH/s, 130 W, power $0.10/kWh
- Cost/day ≈ 130W×24/1000×$0.10 ≈ $0.31
- Revenue/day varies with coin price and difficulty; see pool/what-to-mine.
- Use src/profitability.py to recompute with live inputs.

Warning: For Bitcoin SHA-256, even high-end GPUs are millions of times slower than ASICs; expected profit is negative at typical power rates.

## Setup Details
- scripts/setup.sh: installs dependencies (drivers, docker, nvidia toolkits)
- docker/Dockerfile: minimal CUDA runtime + Python environment
- src/gpu_utils.py: queries nvidia-smi/NVML for power and utilization
- src/miner_manager.py: launches external miners (e.g., nbminer/tt-miner) with your pool URL
- src/profitability.py: profitability math and CLI
- src/main.py: orchestrator (load .env, check GPU, run benchmark/miner, compute profitability)

## Troubleshooting
- No GPUs detected: verify drivers and `nvidia-smi` works; in Docker, install NVIDIA Container Toolkit and run with `--gpus all`.
- Low hashrate: ensure PCIe power limits and clocks; disable power limiters, update miner.
- High power cost: reduce PL, optimize intensity, consider different coins.
- Pool rejects shares: verify wallet, pool URL/port, region latency.
- Docker build fails: check CUDA base image tag matches host driver capability.

## Development
- Format/lint: black, isort, flake8
- Tests: pytest
- CI: add GitHub Actions as needed

## Security and Compliance
- Use at your own risk. Mining may be restricted in your jurisdiction; ensure compliance.
- Keep wallets and keys secure; never commit secrets.

## License
MIT License (see LICENSE)
