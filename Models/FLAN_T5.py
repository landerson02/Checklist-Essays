
import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# Load data into pandas DataFrame
# data_df = pd.read_excel("../StudentEssays.xlsx")

# Initialize T5 tokenizer and model
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

# Move the model to the CUDA device if available
if torch.cuda.is_available():
    model.to("cuda")

# Define a list of concepts to predict
concepts_to_predict = ["potential energy", "kinetic energy", "Law of Conservation of Energy"]

# Define possible outcome labels
outcome_labels = ["Acceptable", "Unacceptable", "Insufficient"]

# Create a list to store predictions as dictionaries
predictions_list = []

# Iterate through each row of text data
# for index, row in data_df.iterrows():
#     text = row['Essay']  # Assuming the text content is in column 'Essay'
# 
#     # Initialize predictions dictionary for this row
#     predictions = {}
# 
#     # Iterate through each concept to predict
#     for concept in concepts_to_predict:
#         # Define a template for classification
#         template = f"According to the following essay, is the student's definition of {concept} Acceptable, Unacceptable, or Insufficient?\n{text}"
# 
#         # Prepare the input by replacing placeholders
#         formatted_input = template
#         # Tokenize and classify the text
#         input_ids = tokenizer(formatted_input, return_tensors="pt", padding=True, truncation=True).input_ids.to("cuda" if torch.cuda.is_available() else "cpu")
#         outputs = model.generate(input_ids, max_length=128)
#         decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)  # Remove special tokens
# 
#         # Store the prediction in the dictionary
#         predictions[concept] = next((label for label in outcome_labels if label in decoded_output), "Unknown")
# 
#     # Append the predictions to the list
#     predictions_list.append(predictions)
# 
# # Convert the list of dictionaries to a DataFrame
# predictions_df = pd.DataFrame(predictions_list)
# 
# # # Print the predictions
# # print(predictions_df)
# # Set options to display all rows and columns
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# 
# # Print the predictions
# print(predictions_df)


def get_results(text):

    # Initialize predictions dictionary for this row
    predictions = {}

    # Iterate through each concept to predict
    for concept in concepts_to_predict:
        # Define a template for classification
        template = f"According to the following essay, is the student's definition of {concept} Acceptable, Unacceptable, or Insufficient?\n{text}"

        # Prepare the input by replacing placeholders
        formatted_input = template
        # Tokenize and classify the text
        input_ids = tokenizer(formatted_input, return_tensors="pt", padding=True, truncation=True).input_ids.to("cuda" if torch.cuda.is_available() else "cpu")
        outputs = model.generate(input_ids, max_length=128)
        decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)  # Remove special tokens

        # Store the prediction in the dictionary
        predictions[concept] = next((label for label in outcome_labels if label in decoded_output), "Unknown")

    # Append the predictions to the list
    return predictions


# get_results("the law of conservation of energy states that total energy can change")

# Update the original DataFrame with the predictions
# data_df["PE"] = predictions_df["potential energy"]
# data_df["KE"] = predictions_df["kinetic energy"]
# data_df["LCE"] = predictions_df["Law of Conservation of Energy"]

# Save the modified DataFrame to the same Excel file, overwriting the original file
# data_df.to_excel("StudentEssays2.xlsx", index=False)
