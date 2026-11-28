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


def run_simulation(seed: int) -> tuple[City, list[dict], int]:
    """Initialize and run the city simulation for NUM_MONTHS steps."""
    random.seed(seed)
    city = City(size=CITY_SIZE, area_rates=AREA_RATES)
    city.initialize()

    # Places owned by hosts from each area of origin, recorded every month.
    ownership_history = [city.places_owned_by_area()]
    total_transactions = 0

    for _ in range(NUM_MONTHS):
        transactions = city.iterate()
        total_transactions += len(transactions)
        ownership_history.append(city.places_owned_by_area())

    return city, ownership_history, total_transactions


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


def plot_graph2_ownership(
    ownership_history: list[dict],
    hosts_without_places: int,
    title: str,
    output_path: Path,
) -> None:
    """Save line chart of places owned by hosts from each area of origin over time."""
    months = range(len(ownership_history))
    n_places = sum(ownership_history[0].values())

    fig, ax = plt.subplots(figsize=(11, 6.5))

    for area in sorted(AREA_LABELS.keys()):
        values = [month[area] for month in ownership_history]
        ax.plot(months, values, color=AREA_COLORS[area], linewidth=2, label=AREA_LABELS[area])
        # Label each line at its end so the chart does not rely on colour alone
        ax.annotate(f"Area {area}: {values[-1]}", xy=(months[-1], values[-1]),
                    xytext=(6, 0), textcoords="offset points", va="center", fontsize=10)

    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=28)
    ax.text(0, 1.02,
            f"Each area starts with 25 of the {n_places} places. "
            f"By month {NUM_MONTHS}, {hosts_without_places} of {n_places} hosts own no property.",
            transform=ax.transAxes, fontsize=9.5, color="#444444")

    ax.set_xlabel("Simulation Month (0–180)")
    ax.set_ylabel(f"Places Owned (of {n_places})")
    ax.set_xlim(0, NUM_MONTHS)
    ax.set_xticks(range(0, NUM_MONTHS + 1, 12))
    # Fixed y-range so graph2_v0 and graph2_v1 can be compared directly
    highest = max(max(month.values()) for month in ownership_history)
    ax.set_ylim(10, max(40, highest + 2))
    ax.legend(title="Host's Area of Origin", loc="upper center", bbox_to_anchor=(0.5, -0.12),
              ncol=4, fontsize=8.5, title_fontsize=9, frameon=False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main() -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Runs whichever rule is active in the code (the original rule, v0).
    city, ownership_history, total_transactions = run_simulation(seed=SEED)

    plot_graph1_wealth(compute_host_wealth(city), reports_dir / "graph1.png")
    plot_graph2_ownership(
        ownership_history=ownership_history,
        hosts_without_places=city.hosts_without_places(),
        title="Who Owns the City? Places Owned by Hosts From Each Area of Origin",
        output_path=reports_dir / "graph2_v0.png",
    )

    print(f"{total_transactions} total trades | "
          f"places owned by area: {ownership_history[-1]} | "
          f"hosts with no property: {city.hosts_without_places()}")


if __name__ == "__main__":
    main()
