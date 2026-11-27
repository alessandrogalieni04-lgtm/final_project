import random
from pathlib import Path
import matplotlib.pyplot as plt
from final_project.city import City

# Set global random seed once for full reproducibility
SEED = 42
random.seed(SEED)

# Simulation parameters from the project brief
CITY_SIZE = 10
NUM_MONTHS = 180
AREA_RATES = {
    0: (100, 200),  # Bottom-left
    1: (50, 250),   # Bottom-right
    2: (250, 350),  # Top-left
    3: (150, 450),  # Top-right
}

AREA_LABELS = {
    0: "Area 0 (Bottom-Left: €100–200)",
    1: "Area 1 (Bottom-Right: €50–250)",
    2: "Area 2 (Top-Left: €250–350)",
    3: "Area 3 (Top-Right: €150–450)",
}

AREA_COLORS = {
    0: "#4E79A7",
    1: "#F28E2B",
    2: "#59A14F",
    3: "#E15759",
}


def compute_top10_share(city: City) -> float:
    """Return the share of all listings owned by the top 10% of hosts."""
    num_hosts = len(city.hosts)
    top_k = max(1, int(0.10 * num_hosts))
    asset_counts = sorted((len(h.assets) for h in city.hosts), reverse=True)
    return sum(asset_counts[:top_k]) / len(city.places)


def compute_host_wealth(city: City) -> list[dict]:
    """Calculate total wealth (cash profits + latest price of owned places) per host."""
    wealth_records = []
    for host in city.hosts:
        property_value = 0.0
        for pid in host.assets:
            place = city.places[pid]
            latest_step = max(place.price.keys())
            property_value += place.price[latest_step]

        total_wealth = host.profits + property_value
        wealth_records.append(
            {
                "host_id": host.host_id,
                "area": host.area,
                "wealth": total_wealth,
                "assets_count": len(host.assets),
            }
        )
    return wealth_records


def run_simulation(seed: int, priority_small_hosts: bool = False) -> tuple[City, list[float], int]:
    """Initialize and run the city simulation for NUM_MONTHS steps."""
    random.seed(seed)
    city = City(
        size=CITY_SIZE,
        area_rates=AREA_RATES,
        priority_small_hosts=priority_small_hosts,
    )
    city.initialize()

    top10_history = [compute_top10_share(city)]
    total_transactions = 0

    for _ in range(NUM_MONTHS):
        transactions = city.iterate()
        total_transactions += len(transactions)
        top10_history.append(compute_top10_share(city))

    return city, top10_history, total_transactions


def plot_graph1_wealth(wealth_records: list[dict], output_path: Path) -> None:
    """Save vertical bar chart of host wealth sorted ascending and colored by origin area."""
    sorted_records = sorted(wealth_records, key=lambda r: r["wealth"])
    x_positions = range(len(sorted_records))
    heights = [r["wealth"] for r in sorted_records]
    colors = [AREA_COLORS[r["area"]] for r in sorted_records]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x_positions, heights, color=colors, width=0.85)

    # Create legend entries for each area of origin
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=AREA_COLORS[area])
        for area in sorted(AREA_LABELS.keys())
    ]
    ax.legend(handles, [AREA_LABELS[a] for a in sorted(AREA_LABELS.keys())], title="Area of Origin")

    ax.set_title("Final Host Wealth After 15 Years (180 Months) by Area of Origin", fontsize=13, fontweight="bold")
    ax.set_xlabel("Hosts (Sorted from Lowest to Highest Total Wealth)")
    ax.set_ylabel("Total Wealth (€: Accumulated Profits + Property Value)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_graph2_concentration(
    top10_history: list[float],
    title: str,
    subtitle: str,
    output_path: Path,
    color: str = "#2B5C8F",
) -> None:
    """Save time-series chart of the share of listings owned by the top 10% of hosts."""
    months = range(len(top10_history))
    percentages = [share * 100 for share in top10_history]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(months, percentages, color=color, linewidth=2.2, label="Top 10% Hosts Ownership Share")
    ax.axhline(10.0, color="gray", linestyle=":", linewidth=1.2, label="Equal Distribution Baseline (10%)")

    ax.set_title(title, fontsize=13, fontweight="bold", pad=22)
    plt.suptitle(subtitle, fontsize=9.5, color="#444444", y=0.93)
    ax.set_xlabel("Simulation Month (0–180)")
    ax.set_ylabel("Share of Total Listings Owned by Top 10% (%)")
    ax.set_xlim(0, NUM_MONTHS)
    ax.set_ylim(0, max(25, max(percentages) + 5))
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main() -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run baseline simulation (v0: sort by spread descending)
    city_v0, top10_v0, tx_v0 = run_simulation(seed=SEED, priority_small_hosts=False)
    wealth_v0 = compute_host_wealth(city_v0)

    plot_graph1_wealth(wealth_v0, reports_dir / "graph1.png")
    plot_graph2_concentration(
        top10_history=top10_v0,
        title="Market Concentration Over Time — Baseline Rule (v0)",
        subtitle="Share of 100 listings held by the top 10 hosts (bids sorted by spread descending)",
        output_path=reports_dir / "graph2_v0.png",
        color="#2B5C8F",
    )

    # 2. Run modified simulation (v1: prioritize hosts with fewer properties)
    city_v1, top10_v1, tx_v1 = run_simulation(seed=SEED, priority_small_hosts=True)
    plot_graph2_concentration(
        top10_history=top10_v1,
        title="Market Concentration Over Time — Small-Host Priority Rule (v1)",
        subtitle="Share of 100 listings held by the top 10 hosts (bids sorted by assets ascending, then spread descending)",
        output_path=reports_dir / "graph2_v1.png",
        color="#D95F02",
    )

    # Diagnostics for Phase 2 check
    print(f"Baseline (v0): {tx_v0} total trades | Final Top-10% Share: {top10_v0[-1]:.1%}")
    print(f"Modified (v1): {tx_v1} total trades | Final Top-10% Share: {top10_v1[-1]:.1%}")


if __name__ == "__main__":
    main()
