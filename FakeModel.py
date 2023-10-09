# %%
import random

class Model:
    def __init__(self, input_string):
        self.input_string = input_string

    def __call__(self):
        random_values = {
            'PE': self.getRandomCategory(),
            'KE': self.getRandomCategory(),
            'LCE': self.getRandomCategory(),
        }
        return random_values

    def getRandomCategory(self):
        num = random.random()
        if num < .333:
            return "Acceptable"
        elif num < .666:
            return "Unacceptable"
        else:
            return "Insufficient"

# # Example usage:
# if __name__ == "__main__":
#     model_instance = Model("example_input")
#     result = model_instance()
#     print(result)

# %%
