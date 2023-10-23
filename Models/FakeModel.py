import random


class Model:
    def __init__(self, input_string):
        self.input_string = input_string

    def __call__(self):
        random_values = {
            'PE': self.getRandomCategory(),
            'KE': self.getRandomCategory(),
            'LCE': self.getRandomCategory(),
            'NF': self.getRandomCategory(),
        }
        return random_values

    def getRandomCategory(self):
        num = random.random()
        if num < .25:
            return "Acceptable"
        elif num < .5:
            return "Unacceptable"
        elif num < .75:
            return "Insufficient"
        else:
            return "Not Found"

