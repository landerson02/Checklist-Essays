import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch


class Flan:

    # Initialize variables upon instantiation
    def __init__(self):
        # Initialize T5 tokenizer and model
        self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
        self.model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

        # Move the model to the CUDA device if available
        if torch.cuda.is_available():
            self.model.to("cuda")

        # Define a list of concepts to predict
        self.concepts_to_predict = ["potential energy", "kinetic energy", "Law of Conservation of Energy"]

        # Define possible outcome labels
        self.outcome_labels = ["Acceptable", "Unacceptable", "Insufficient"]

        # Create a list to store predictions as dictionaries
        self.predictions_list = []

    def get_results(self, text):

        # Initialize predictions dictionary for this row
        predictions = {}
        # Iterate through each concept to predict
        for concept in self.concepts_to_predict:
            # Define a template for classification
            template = f"According to the following essay, is the student's definition of {concept} Acceptable, " \
                       f"Unacceptable, Insufficient?\n{text}"

            # Prepare the input by replacing placeholders
            formatted_input = template
            # Tokenize and classify the text
            input_ids = self.tokenizer(formatted_input, return_tensors="pt", padding=True, truncation=True)\
                .input_ids.to("cuda" if torch.cuda.is_available() else "cpu")

            outputs = self.model.generate(input_ids, max_length=128)
            decoded_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)  # Remove special tokens

            # Map to rename concepts to abbreviation
            rename = {"potential energy": "PE",
                      "kinetic energy": "KE",
                      "Law of Conservation of Energy": "LCE"
                      }
            # Store the prediction in the dictionary
            predictions[rename[concept]] = \
                next((label for label in self.outcome_labels if label in decoded_output), "Unknown")

        # Append the predictions to the list
        return predictions

