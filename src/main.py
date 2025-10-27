import os
from dotenv import load_dotenv
from src.profitability import estimate_profit
from src.gpu_utils import gpu_summary


def main():
    load_dotenv()
    print("GPU Mining Automation - bootstrap")
    print(gpu_summary())
    profit = estimate_profit(
        algo=os.getenv("TARGET_ALGO", "KAWPOW"),
        hashrate=float(os.getenv("HASHRATE_MH", "26")),
        power_watts=float(os.getenv("POWER_WATTS", "130")),
        power_cost=float(os.getenv("POWER_COST_USD_PER_KWH", "0.10")),
        pool_fee=float(os.getenv("POOL_FEE", "0.01")),
    )
    print(f"Estimated daily profit (USD): {profit:.2f}")


if __name__ == "__main__":
    main()
