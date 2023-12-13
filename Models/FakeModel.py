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
        if num < .5:
            return "Acceptable"
        return "Unacceptable"

    def get_results(self, sample):
        return self.__call__()
