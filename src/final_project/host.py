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
