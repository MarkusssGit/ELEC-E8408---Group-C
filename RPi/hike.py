MET_HIKING = 6
KCAL_PER_STEP = 0.04

class HikeSession:
    id = 0
    km = 0
    steps = 0
    kcal = -1
    coords = []

    # represents a computationally intensive calculation done by lazy execution.
    def calc_kcal(self):
        self.kcal = MET_HIKING * KCAL_PER_STEP * self.steps

    def __repr__(self):
        return f"HikeSession{{{self.id}, {self.km}(km), {self.steps}(steps), {self.kcal:.2f}(kcal)}}"

def to_list(s: HikeSession) -> list:
    return [s.id, s.km, s.steps, s.kcal]

def from_list(l: list) -> HikeSession:
    s = HikeSession()
    s.id = l[0]
    s.km = l[1]
    s.steps = l[2]
    s.kcal = l[3]
    return s