
def predict_essay_result(essay, model, tokenizer, concept):
    prompt = f"According to the following essay, classify the student's definition of {concept} as {{option_1: Acceptable}}, {{option_2: Unacceptable}}, {{option_3: Insufficient}}, or {{option_4: Not Found}}\n{essay}"
    inputs = tokenizer(prompt, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
    outputs = model.generate(inputs['input_ids'], attention_mask=inputs['attention_mask'], max_new_tokens=50)  # Adjust max_new_tokens as needed
    prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return prediction


def get_results(sample):
    # Make sure the models and tokenizers are loaded
    pe_model, pe_tokenizer = tf.keras.models.load_model('model_PE')
    ke_model, ke_tokenizer = tf.keras.models.load_model('model_KE')
    lce_model, lce_tokenizer = tf.keras.models.load_model('model_LCE')
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
example = "put anything here"
get_results(example)
