import pandas as pd


class City:
    def __init__(self, size, area_rates):
        self.size = size
        self.area_rates = area_rates
        self.step = 0
        self.places = []
        self.hosts = []

    def initialize(self):
        # Imported here so city.py can be tested before place.py and host.py exist.
        from final_project.place import Place
        from final_project.host import Host

        n_places = self.size * self.size

        # One place per grid cell. At the start, host i owns place i.
        self.places = [Place(pid, pid, self) for pid in range(n_places)]
        for place in self.places:
            place.setup()

        # One host per place, created after setup() so place.area is known.
        self.hosts = [Host(place.host_id, place, self) for place in self.places]

    def approve_bids(self, bids):
        if not bids:
            return []

        df = pd.DataFrame(bids)

        # Original rule (v0): most competitive bids first.
        # "stable" keeps ties in a fixed order.
        df = df.sort_values("spread", ascending=False, kind="stable")

        # Modified rule (v1): buyers with fewer properties first,
        # then the most competitive bids. Used to make graph2_v1.png.
        # df["buyer_assets"] = [len(self.hosts[b].assets) for b in df["buyer_id"]]
        # df = df.sort_values(["buyer_assets", "spread"],
        #                     ascending=[True, False], kind="stable")

        buyers_done = set()
        places_sold = set()
        approved = []

        for bid in df.to_dict("records"):
            # A buyer buys at most one place, and a place is sold at most once.
            if bid["buyer_id"] in buyers_done or bid["place_id"] in places_sold:
                continue
            approved.append(bid)
            buyers_done.add(bid["buyer_id"])
            places_sold.add(bid["place_id"])

        return approved

    def execute_transactions(self, transactions):
        for t in transactions:
            buyer = self.hosts[t["buyer_id"]]
            seller = self.hosts[t["seller_id"]]
            place = self.places[t["place_id"]]
            price = t["bid_price"]

            # Money moves from buyer to seller.
            buyer.profits -= price
            seller.profits += price

            # Ownership moves from seller to buyer.
            seller.assets.remove(place.place_id)
            # Remembered for the modified rule in Host.make_bids (v1).
            # It changes nothing under the original rule.
            seller.last_place = place.place_id
            buyer.assets.add(place.place_id)
            place.host_id = buyer.host_id

            # Record the sale price at this step.
            place.price[self.step] = price

    def clear_market(self):
        bids = []
        for host in self.hosts:
            bids.extend(host.make_bids())

        transactions = self.approve_bids(bids)
        if transactions:
            self.execute_transactions(transactions)
        return transactions

    def places_owned_by_area(self):
        # Number of places owned by hosts from each area of origin.
        # Used for graph2. Starts at 25 per area on a 10x10 grid.
        counts = {area: 0 for area in self.area_rates}
        for host in self.hosts:
            counts[host.area] += len(host.assets)
        return counts

    def hosts_without_places(self):
        # Hosts who have sold everything. They can no longer bid,
        # because bids only go to neighbours of places they own.
        return sum(1 for host in self.hosts if not host.assets)

    def iterate(self):
        self.step += 1
        for place in self.places:
            place.update_occupancy()
        for host in self.hosts:
            host.update_profits()
        return self.clear_market()
