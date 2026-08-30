class StressState:
    def __init__(self):
        self.level = 0        # 0–100
        self.trend = 0        # rising or falling
        self.sources = []     # list of contributing events

    def apply(self, amount, source):
        self.level = max(0, min(100, self.level + amount))
        self.sources.append(source)
        self.trend = amount
