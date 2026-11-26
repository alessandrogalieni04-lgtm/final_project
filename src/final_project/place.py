import random

class Place:

    def __init__(self, place_id, host_id, city):
        self.place_id = place_id
        self.host_id = host_id
        self.city = city

    def setup(self):
        n = self.city.size
        x = self.place_id % n
        y = self.place_id // n

        neighbours = [
            (x-1, y-1), (x, y-1), (x+1, y-1),
            (x-1, y),             (x+1, y),
            (x-1, y+1), (x, y+1), (x+1, y+1)
        ]

        self.neighbours = [
            i + j*n for i, j in neighbours
            if 0 <= i < n and 0 <= j < n
        ]

        half = n // 2
        self.area = int(x >= half) + 2 * int(y >= half)

        low, high = self.city.area_rates[self.area]
        self.rate = random.uniform(low, high)
        self.price = {0: 900 * self.rate}

    def update_occupancy(self):
        area_rates = [
            place.rate for place in self.city.places
            if place.area == self.area
        ]

        mean_rate = sum(area_rates) / len(area_rates)

        if self.rate > mean_rate:
            self.occupancy = random.randint(5, 15)
        else:
            self.occupancy = random.randint(10, 20)
