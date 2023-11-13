# -*- coding: utf-8 -*-
"""FLAN_T5_Training_v2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1P89ochHCRPHXMQMl5nl7lWXONoGLwPjI
"""

import locale
locale.getpreferredencoding = lambda: "UTF-8"

# !pip install transformers
#
# !pip install sentencepiece
#
# !pip install accelerate

from transformers import T5Tokenizer, T5ForConditionalGeneration

import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:50'
import pandas as pd
import torch
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from transformers import Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
import numpy as np

# Initialize T5 tokenizer
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")

# Define the outcome_labels
outcome_labels = ["acceptable", "unacceptable", "insufficient", "not found"]

# Standardize the labels
data_df = pd.read_excel("Student Essays Final Annotations.xlsx")
data_df["PE"] = data_df["PE"].str.lower().str.strip()
data_df["KE"] = data_df["KE"].str.lower().str.strip()
data_df["LCE"] = data_df["LCE"].str.lower().str.strip()

# Initialize 5-fold cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)
# Define the custom dataset with prompts


class EssayDatasetWithPrompt(Dataset):
    def __init__(self, essays, concept, labels, tokenizer, max_length=512):
        self.essays = essays
        self.concept = concept
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.essays)

    def __getitem__(self, idx):
      essay = self.essays[idx]
      label = self.labels[idx]  # This is now a string like "acceptable"
      #prompt = f"According to the following essay, is the student's definition of {self.concept} Acceptable, Unacceptable, Insufficient, or Not Found? Only use one of these labels for outputs\n{essay}"
      prompt = f"According to the following essay, classify the student's definition of {self.concept} as {{option_1: Acceptable}}, {{option_2: Unacceptable}}, {{option_3: Insufficient}}, or {{option_4: Not Found}}\n{essay}"
      inputs = self.tokenizer(prompt, return_tensors="pt", padding="max_length", truncation=True, max_length=self.max_length)

      # Tokenize the label
      label_tokens = self.tokenizer(label, return_tensors="pt", padding="max_length", truncation=True, max_length=self.max_length)["input_ids"].squeeze()

      return {
        'input_ids': inputs['input_ids'].squeeze(0),
        'attention_mask': inputs['attention_mask'].squeeze(0),
        'labels': label_tokens
      }

# Fine-tuning function
def fine_tune_with_prompt(concept, data_df, model_path=None):
    # Load or initialize the model
    if model_path:
        model = T5ForConditionalGeneration.from_pretrained(model_path)
    else:
        model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
    if torch.cuda.is_available():
        model.to("cuda")

    # Prepare training arguments
    training_args = TrainingArguments(
        output_dir=f'./results_{concept}',
        num_train_epochs=8,
        per_device_train_batch_size=2,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_dir='./logs',
        logging_steps=10,
        learning_rate=5e-5,
        load_best_model_at_end=True,
        metric_for_best_model='loss',
        greater_is_better=False,
        warmup_steps=500,
        weight_decay=0.01,
        save_total_limit=1
    )

    # KFold cross-validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    for fold, (train_idx, val_idx) in enumerate(kf.split(data_df)):
        print(f"Training fold {fold + 1} for {concept}...")

        # Prepare datasets for the current fold
        train_dataset = EssayDatasetWithPrompt(data_df['Essay'].iloc[train_idx].values, concept, data_df[concept].iloc[train_idx].values, tokenizer)
        val_dataset = EssayDatasetWithPrompt(data_df['Essay'].iloc[val_idx].values, concept, data_df[concept].iloc[val_idx].values, tokenizer)

        # Initialize Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )

        # Train the model
        trainer.train()

        # Save the model
        model_save_path = f'./model_{concept}_best'
        model.save_pretrained(model_save_path)
        tokenizer.save_pretrained(model_save_path)

    return model_save_path

# Standardize the labels and load data
data_df = pd.read_excel("Student Essays Final Annotations.xlsx")
data_df["PE"] = data_df["PE"].str.lower().str.strip()
data_df["KE"] = data_df["KE"].str.lower().str.strip()
data_df["LCE"] = data_df["LCE"].str.lower().str.strip()

# Train and save the model for each concept and revisit PE
pe_path = fine_tune_with_prompt("PE", data_df)
ke_path = fine_tune_with_prompt("KE", data_df, model_path=pe_path)
lce_path = fine_tune_with_prompt("LCE", data_df, model_path=ke_path)
fine_tune_with_prompt("PE", data_df, model_path=lce_path)
fine_tune_with_prompt("KE", data_df, model_path=lce_path)
fine_tune_with_prompt("LCE", data_df, model_path=lce_path)

from transformers import T5ForConditionalGeneration, T5Tokenizer

# Function to load a model
def load_model(model_name):
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model.eval()
    return model, tokenizer

# Function to predict the label for an essay
def predict_label(essay, model, tokenizer, concept):
    prompt = f"According to the following essay, classify the student's definition of {concept} as {{option_1: Acceptable}}, {{option_2: Unacceptable}}, {{option_3: Insufficient}}, or {{option_4: Not Found}}\n{essay}"
    inputs = tokenizer(prompt, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
    outputs = model.generate(inputs['input_ids'], attention_mask=inputs['attention_mask'], max_new_tokens=50)  # Adjust max_new_tokens as needed
    prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return prediction

# Load the dataset
data_df = pd.read_excel("Student Essays Final Annotations.xlsx")

# Load each model
pe_model, pe_tokenizer = load_model('model_PE_best')
ke_model, ke_tokenizer = load_model('model_KE_best')
lce_model, lce_tokenizer = load_model('model_LCE_best')

# DataFrame creation
results_df = pd.DataFrame(columns=['Essay ID', 'PE_Actual', 'PE_Predicted', 'KE_Actual', 'KE_Predicted', 'LCE_Actual', 'LCE_Predicted'])

# Iterate over the dataset and predict labels
for index, row in data_df.iterrows():
    pe_pred = predict_label(row['Essay'], pe_model, pe_tokenizer, 'PE')
    ke_pred = predict_label(row['Essay'], ke_model, ke_tokenizer, 'KE')
    lce_pred = predict_label(row['Essay'], lce_model, lce_tokenizer, 'LCE')

    new_row = pd.DataFrame({'Essay ID': [row['Essay ID']],
                            'PE_Actual': [row['PE']], 'PE_Predicted': [pe_pred],
                            'KE_Actual': [row['KE']], 'KE_Predicted': [ke_pred],
                            'LCE_Actual': [row['LCE']], 'LCE_Predicted': [lce_pred]})
    results_df = pd.concat([results_df, new_row], ignore_index=True)

# Save the DataFrame to a CSV file
results_csv_path = "./predictions_vs_actuals.csv"
results_df.to_csv(results_csv_path, index=False)

from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support, roc_auc_score, classification_report

results_df = pd.read_csv('predictions_vs_actuals.csv')
results_df['PE_Actual'] = results_df['PE_Actual'].str.lower()
results_df['PE_Predicted'] = results_df['PE_Predicted'].str.lower()
results_df['KE_Actual'] = results_df['KE_Actual'].str.lower()
results_df['KE_Predicted'] = results_df['KE_Predicted'].str.lower()
results_df['LCE_Actual'] = results_df['LCE_Actual'].str.lower()
results_df['LCE_Predicted'] = results_df['LCE_Predicted'].str.lower()

# Define a function to calculate metrics
def calculate_metrics(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=1)

    # Precision, Recall for each class
    precision, recall, _, _ = precision_recall_fscore_support(y_true, y_pred, labels=["acceptable", "unacceptable", "insufficient", "not found"], zero_division=1)

    # Classification report for detailed metrics
    class_report = classification_report(y_true, y_pred, labels=["acceptable", "unacceptable", "insufficient", "not found"], zero_division=1)

    return accuracy, f1, precision, recall, class_report

# Calculate for PE
accuracy_pe, f1_pe, precision_pe, recall_pe, report_pe = calculate_metrics(results_df['PE_Actual'], results_df['PE_Predicted'])

# Calculate for KE
accuracy_ke, f1_ke, precision_ke, recall_ke, report_ke = calculate_metrics(results_df['KE_Actual'], results_df['KE_Predicted'])

# Calculate for LCE
accuracy_lce, f1_lce, precision_lce, recall_lce, report_lce = calculate_metrics(results_df['LCE_Actual'], results_df['LCE_Predicted'])

# Print the results
print("Metrics for PE:")
print(f"Accuracy: {accuracy_pe}, F1 Score: {f1_pe}")
print(f"Precision: {precision_pe}, Recall: {recall_pe}")
print(f"Classification Report:\n{report_pe}")

print("\nMetrics for KE:")
print(f"Accuracy: {accuracy_ke}, F1 Score: {f1_ke}")
print(f"Precision: {precision_ke}, Recall: {recall_ke}")
print(f"Classification Report:\n{report_ke}")

print("\nMetrics for LCE:")
print(f"Accuracy: {accuracy_lce}, F1 Score: {f1_lce}")
print(f"Precision: {precision_lce}, Recall: {recall_lce}")
print(f"Classification Report:\n{report_lce}")

def predict_essay_result(essay, model, tokenizer, concept):
    prompt = f"According to the following essay, classify the student's definition of {concept} as {{option_1: Acceptable}}, {{option_2: Unacceptable}}, {{option_3: Insufficient}}, or {{option_4: Not Found}}\n{essay}"
    inputs = tokenizer(prompt, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
    outputs = model.generate(inputs['input_ids'], attention_mask=inputs['attention_mask'], max_new_tokens=50)  # Adjust max_new_tokens as needed
    prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return prediction


def get_results(sample):
    # Make sure the models and tokenizers are loaded
    pe_model, pe_tokenizer = load_model('model_PE_best')
    ke_model, ke_tokenizer = load_model('model_KE_best')
    lce_model, lce_tokenizer = load_model('model_LCE_best')

    # Predict labels using the models
    pe_label = predict_essay_result(sample, pe_model, pe_tokenizer, 'PE')
    ke_label = predict_essay_result(sample, ke_model, ke_tokenizer, 'KE')
    lce_label = predict_essay_result(sample, lce_model, lce_tokenizer, 'LCE')

    # Compile the results into a dictionary
    results = {
        "PE": pe_label,
        "KE": ke_label,
        "LCE": lce_label
    }

    return results

essay_1 = ('For the car lift we decided that the car would be .4 kg in weight. The height is 1 m. We chose this height'
           ' because it gave us the most potential energy to work with which was 3.8 Joules. We wanted as much potential'
           ' energy as possible so that we knew it would make it over all the hills and through all the loops. Because'
           ' of the Law of Conservation of Energy, which states that energy can’t be created or destroyed, the car still'
           ' has the same amount of energy at the bottom as it did al the top of the drop. At the top of the drop, '
           'the car had 3.8 Joules of potential energy. At the end the car still has 3.8 Joules of energy, but instead'
           ' of being in a useable form, it is in the unusable form of heat energy.')
get_results(essay_1)

# !pwd
# !zip -r /content/models_v2.zip ./model_KE_best ./model_LCE_best ./model_PE_best