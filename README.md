# GPU Mining Automation

Automate GPU mining on CUDA-capable cards with setup, monitoring, and profitability assessment. This project demonstrates why Bitcoin SHA-256 mining on GPUs is not economical in 2025 while providing tooling to benchmark GPUs, mine alternative GPU-friendly coins, and calculate profitability with electricity costs.

## Key Features

- Setup scripts and Dockerized environment for reproducible runs
- GPU detection, benchmarking (hashrate, power), and monitoring
- Profitability calculator with electricity cost, pool fees, and coin difficulty
- Templates for miners (e.g., kawpow, ethash, equihash) via external miners
- Alerting hooks and run logs
- **Earning-ready automation** with pool connectivity and real-time monitoring

## How to Earn

### Quick Start Earning Guide

1. **Set up your wallet**
   - Create a Ravencoin (RVN) wallet using [Exodus](https://www.exodus.com/) or [Ravencoin Core](https://ravencoin.org/wallet/)
   - Get your wallet address (starts with 'R')
   - Alternative coins: ETC (Ethereum Classic), ZEC (Zcash)

2. **Configure your mining setup**
   ```bash
   git clone https://github.com/zubairansari-codes/gpu-mining-automation.git
   cd gpu-mining-automation
   cp .env.example .env
   ```

3. **Edit .env with your earning details**
   ```
   WALLET_ADDRESS=RYourRavencoinWalletAddressHere
   POOL_URL=stratum+tcp://rvn.2miners.com:6060
   COIN=RVN
   WORKER_NAME=miner01
   PAYOUT_THRESHOLD=10
   ```

4. **Start earning**
   ```bash
   # With Docker (recommended)
   docker build -t gpu-mining-automation -f docker/Dockerfile .
   docker run --gpus all --env-file .env --rm gpu-mining-automation
   
   # Or locally
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   python src/main.py
   ```

### Pool Configuration

**Ravencoin (RVN) - Default Setup**
- Pool: 2Miners (rvn.2miners.com:6060)
- Algorithm: KAWPOW
- Minimum payout: 1 RVN
- Fee: 1%

**Ethereum Classic (ETC)**
- Pool: 2Miners (etc.2miners.com:1010)
- Algorithm: ETHASH
- Minimum payout: 0.01 ETC

**Zcash (ZEC)**
- Pool: 2Miners (zec.2miners.com:1010)
- Algorithm: Equihash
- Minimum payout: 0.001 ZEC

### Earning Monitoring

The system automatically:
- Connects to your chosen pool
- Monitors hashrate and accepted shares
- Logs earning events and pool stats
- Calculates real-time profitability
- Handles miner restarts on failures

View your earnings at:
- RVN: https://rvn.2miners.com/account/YOUR_WALLET_ADDRESS
- ETC: https://etc.2miners.com/account/YOUR_WALLET_ADDRESS
- ZEC: https://zec.2miners.com/account/YOUR_WALLET_ADDRESS

### Expected Daily Earnings (Estimates)

**RTX 3060 Ti (130W, $0.10/kWh power)**
- RVN: ~26 MH/s → $1.50-3.00/day (varies with price)
- Power cost: ~$0.31/day
- Net profit: $1.19-2.69/day

**GTX 1660 Super (125W)**
- RVN: ~14 MH/s → $0.80-1.60/day
- Power cost: ~$0.30/day
- Net profit: $0.50-1.30/day

*Note: Earnings fluctuate with coin prices, network difficulty, and pool luck. Always verify current rates.*

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
│  ├─ miner_manager.py      # Launch miners, connect to pools, handle restarts
│  ├─ profitability.py      # Real earnings tracking with pool API stats
│  ├─ gpu_utils.py
│  └─ config.py
├─ scripts/
│  ├─ setup.sh
│  └─ quick_start.sh
├─ .env.example             # Sample earning-ready configuration
├─ .gitignore
└─ README.md
```

## Quick Start

### Prerequisites

- NVIDIA GPU with recent CUDA drivers
- Docker + NVIDIA Container Toolkit (or Python 3.10+ with nvml/nvidia-smi)
- Mining pool credentials for your target coin

### Clone and configure

```bash
git clone https://github.com/zubairansari-codes/gpu-mining-automation.git
cd gpu-mining-automation
cp .env.example .env
# Edit .env values (wallet address, pool URL, power cost, etc.)
```

### Run with Docker

```bash
docker build -t gpu-mining-automation -f docker/Dockerfile .
docker run --gpus all --env-file .env --rm gpu-mining-automation
```

### Or run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Configuration (.env)

### Earning-Ready Fields

- `WALLET_ADDRESS=` - Your cryptocurrency wallet address
- `POOL_URL=stratum+tcp://pool:port` - Mining pool connection string
- `COIN=RVN|ETC|ZEC` - Target cryptocurrency
- `WORKER_NAME=` - Unique identifier for this mining rig
- `PAYOUT_THRESHOLD=` - Minimum earning before payout
- `POWER_COST_USD_PER_KWH=0.05` - Your electricity rate
- `TARGET_ALGO=KAWPOW|ETHASH|EQUIHASH` - Mining algorithm
- `LOG_LEVEL=INFO` - Logging verbosity

## Profitability Calculations

The calculator estimates daily profit with real pool API integration:

- Revenue/day = hashrate × network_factor(coin, algo, difficulty, block_reward, price)
- Cost/day = power_watts × 24/1000 × power_cost  
- Profit/day = Revenue/day − Cost/day − Pool fees
- **Real earnings tracking** from pool API statistics

Example (illustrative):
- RTX 3060 Ti @ KAWPOW ~ 26 MH/s, 130 W, power $0.10/kWh
- Cost/day ≈ 130W×24/1000×$0.10 ≈ $0.31
- Revenue/day varies with coin price and difficulty; see pool/what-to-mine.
- Use `src/profitability.py` to recompute with live inputs.

**Warning:** For Bitcoin SHA-256, even high-end GPUs are millions of times slower than ASICs; expected profit is negative at typical power rates.

## Setup Details

- `scripts/setup.sh`: installs dependencies (drivers, docker, nvidia toolkits)
- `docker/Dockerfile`: minimal CUDA runtime + Python environment
- `src/gpu_utils.py`: queries nvidia-smi/NVML for power and utilization
- `src/miner_manager.py`: launches external miners (e.g., nbminer/tt-miner) with your pool URL
- `src/profitability.py`: profitability math and CLI with real pool API integration
- `src/main.py`: orchestrator (load .env, check GPU, run benchmark/miner, compute profitability)

## Troubleshooting

- **No GPUs detected**: verify drivers and `nvidia-smi` works; in Docker, install NVIDIA Container Toolkit and run with `--gpus all`.
- **Low hashrate**: ensure PCIe power limits and clocks; disable power limiters, update miner.
- **High power cost**: reduce PL, optimize intensity, consider different coins.
- **Pool rejects shares**: verify wallet, pool URL/port, region latency.
- **Docker build fails**: check CUDA base image tag matches host driver capability.
- **No earnings showing**: check wallet address format, pool connection, and miner status logs.

## Development

- Format/lint: black, isort, flake8
- Tests: pytest
- CI: add GitHub Actions as needed

## Security and Compliance

- Use at your own risk. Mining may be restricted in your jurisdiction; ensure compliance.
- Keep wallets and keys secure; never commit secrets.

## License

MIT License (see LICENSE)
