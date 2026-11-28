class Host:
    """An owner and their available funds in the city simulation."""

    def __init__(self, host_id, place, city, profits=0):
        self.host_id = host_id
        self.city = city
        self.profits = profits
        self.area = place.area
        self.assets = {place.place_id}

    def update_profits(self):
        """Add one month's rental income from the host's properties."""
        for place_id in self.assets:
            place = self.city.places[place_id]
            self.profits += place.rate * place.occupancy
    def make_bids(self):
        """Return bids for neighbouring properties the host can afford."""
        opportunities = set()

        # Original rule (v0): only look next to places the host owns now.
        # A host that has sold everything has no neighbours and can never bid.
        search_from = self.assets

        # Modified rule (v1): a host that has sold everything can still
        # bid on places next to the last place it owned.
        # search_from = self.assets if self.assets else {self.last_place}

        for place_id in search_from:
            place = self.city.places[place_id]
            for neighbour_id in place.neighbours:
                if neighbour_id not in self.assets:
                    opportunities.add(neighbour_id)

        bids = []
        for place_id in sorted(opportunities):
            place = self.city.places[place_id]
            last_sale_step = max(place.price)
            ask_price = place.price[last_sale_step]

            if self.profits >= ask_price:
                bids.append({
                    "place_id": place_id,
                    "seller_id": place.host_id,
                    "buyer_id": self.host_id,
                    "spread": self.profits - ask_price,
                    "bid_price": self.profits
                })

        return bids
