from transformers import T5Tokenizer, T5ForConditionalGeneration


class Flan:
    #
    # # Initialize variables upon instantiation
    # def __init__(self):
    #     # Initialize T5 tokenizer and model
    #     self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
    #     self.model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
    #
    #     # Move the model to the CUDA device if available
    #     if torch.cuda.is_available():
    #         self.model.to("cuda")
    #
    #     # Define a list of concepts to predict
    #     self.concepts_to_predict = ["potential energy", "kinetic energy", "Law of Conservation of Energy"]
    #
    #     # Define possible outcome labels
    #     self.outcome_labels = ["Acceptable", "Unacceptable", "Insufficient", "Not Found"]
    #
    #     # Create a list to store predictions as dictionaries
    #     self.predictions_list = []
    #
    # def get_results(self, text):
    #
    #     # Initialize predictions dictionary for this row
    #     predictions = {}
    #     # Iterate through each concept to predict
    #     for concept in self.concepts_to_predict:
    #         # Define a template for classification
    #         template = f"According to the following essay, is the student's definition of {concept} Acceptable, " \
    #                    f"Unacceptable, Insufficient, or Not Found?\n{text}"
    #
    #         # Prepare the input by replacing placeholders
    #         formatted_input = template
    #         # Tokenize and classify the text
    #         input_ids = self.tokenizer(formatted_input, return_tensors="pt", padding=True, truncation=True)\
    #             .input_ids.to("cuda" if torch.cuda.is_available() else "cpu")
    #
    #         outputs = self.model.generate(input_ids, max_length=128)
    #         decoded_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)  # Remove special tokens
    #
    #         # Map to rename concepts to abbreviation
    #         rename = {"potential energy": "PE",
    #                   "kinetic energy": "KE",
    #                   "Law of Conservation of Energy": "LCE"
    #                   }
    #         # Store the prediction in the dictionary
    #         predictions[rename[concept]] = \
    #             next((label for label in self.outcome_labels if label in decoded_output), "Unknown")
    #
    #     # Append the predictions to the list
    #     return predictions

    def __init__(self):
        self.pe_model, self.pe_tokenizer = self.load_model('Models/FLAN_T5_Models/model_PE')
        self.ke_model, self.ke_tokenizer = self.load_model('Models/FLAN_T5_Models/model_KE')
        self.lce_model, self.lce_tokenizer = self.load_model('Models/FLAN_T5_Models/model_LCE')

    def load_model(self, model_name):
        model = T5ForConditionalGeneration.from_pretrained(model_name)
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model.eval()
        return model, tokenizer

    def predict_essay_result(self, essay, model, tokenizer, concept):
        prompt = f"According to the following essay, classify the student's definition of {concept} as {{option_1: Acceptable}}, {{option_2: Unacceptable}}, {{option_3: Insufficient}}, or {{option_4: Not Found}}\n{essay}"
        inputs = tokenizer(prompt, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
        outputs = model.generate(inputs['input_ids'], attention_mask=inputs['attention_mask'],
                                 max_new_tokens=50)  # Adjust max_new_tokens as needed
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return prediction

    def get_results(self, sample):
        # # Make sure the models and tokenizers are loaded
        # pe_model, pe_tokenizer = self.load_model('model_PE')
        # ke_model, ke_tokenizer = self.load_model('model_KE')
        # lce_model, lce_tokenizer = self.load_model('model_LCE')
        # Predict labels using the models
        pe_label = self.predict_essay_result(sample, self.pe_model, self.pe_tokenizer, 'PE')
        ke_label = self.predict_essay_result(sample, self.ke_model, self.ke_tokenizer, 'KE')
        lce_label = self.predict_essay_result(sample, self.lce_model, self.lce_tokenizer, 'LCE')
        # Compile the results into a dictionary
        results = {
            "PE": pe_label,
            "KE": ke_label,
            "LCE": lce_label
        }
        return results
