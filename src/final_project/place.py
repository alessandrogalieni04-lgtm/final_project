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

        self.neighbours = []
        for j in range(y - 1, y + 2):
            for i in range(x - 1, x + 2):
                if 0 <= i < n and 0 <= j < n and (i, j) != (x, y):
                    self.neighbours.append(i + j * n)

        half = n // 2
        self.area = int(x >= half) + 2 * int(y >= half)
        low, high = self.city.area_rates[self.area]
        self.rate = random.uniform(low, high)
        self.price = {0: 900 * self.rate}

    def update_occupancy(self):
        area_rates = [p.rate for p in self.city.places if p.area == self.area]
        mean_rate = sum(area_rates) / len(area_rates)

        if self.rate > mean_rate:
            self.occupancy = random.randint(5, 15)
        else:
            self.occupancy = random.randint(10, 20)
