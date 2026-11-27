# final_project



This repository contains our group's final project for Programming I, combining an agent-based real estate market simulation with an empirical analysis of host concentration in Barcelona and Madrid using Inside Airbnb data .

## Group Members

| Role | Full Name | GitHub Username |
| :--- | :--- | :--- |
| Member 1 | `Alessandro Galieni` | `@alessandrogalieni04-lgtm` |
| Member 2 | `Emanuele Negretti` | `@emanuelenegretti01-bit` |
| Member 3 | `Xingan Lin` | `@xinganlin01` |
| Member 4 | `Luan Maliku` | `@luanm01a` |

## Datasets (Inside Airbnb)

Our empirical analysis in `notebooks/part2.ipynb` compares host ownership concentration across room types (`Entire home/apt` vs. `Private room`) in Barcelona and Madrid using the 17 September 2026 Inside Airbnb quarterly release:

1. **Barcelona (17 September 2026):** 
   Download: https://data.insideairbnb.com/spain/catalonia/barcelona/2026-09-17/data/listings.csv.gz  
   Save into `data/` as: **`data/barcelona_listings.csv.gz`**
2. **Madrid (17 September 2026):**  
   Download: https://data.insideairbnb.com/spain/comunidad-de-madrid/madrid/2026-09-17/data/listings.csv.gz  
   Save into `data/` as: **`data/madrid_listings.csv.gz`**

*(Note: Both files download with the default filename `listings.csv.gz` from Inside Airbnb and must be renamed as shown above inside `data/` before running the notebook.)*

## Repository Structure

```text
data/
  .gitkeep
notebooks/
  part2.ipynb
reports/
  graph1.png
  graph2_v0.png
  graph2_v1.png
  graph3.png
  presentation.pdf
src/
  final_project/
    __init__.py
    city.py
    host.py
    place.py
.gitignore
environment.yml
pyproject.toml
main.py
README.md
