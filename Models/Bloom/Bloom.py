import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class Bloom:
    def __init__(self):
        # Name of the model
        model_name_PE = "./bloom1b1-full-finetuned-studentessay-PE"
        model_name_KE = "./bloom1b1-full-finetuned-studentessay-KE"
        model_name_LCE = "./bloom1b1-full-finetuned-studentessay-LCE"

        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_PE)
        self.model_PE = AutoModelForCausalLM.from_pretrained(model_name_PE)
        self.model_KE = AutoModelForCausalLM.from_pretrained(model_name_KE)
        self.model_LCE = AutoModelForCausalLM.from_pretrained(model_name_LCE)

    # This function receive a string, prompt, and outputs the string which is
    # the output from the model (note: this includes the original prompt)
    def bloom_output(self, prompt, topic):
        if topic == 'PE':
            model = self.model_PE
        elif topic == 'KE':
            model = self.model_KE
        else:
            model = self.model_LCE
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device).input_ids
        modelx = model.to(self.device)
        outputs = modelx.generate(inputs,
                                  max_new_tokens=10,
                                  do_sample=True,
                                  top_k=50, top_p=0.95,
                                  # temperature=1,
                                  )
        output = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return output

    def prepare_prompt(self, essay, topic):
        topic_full = {
            'PE': "potential energy",
            'KE': "kinetic energy",
            'LCE': "law of conservation of energy"
        }
        prompt = f'''----------
    ESSAY
    ----------
    {essay}
    ----------

    Is the essay acceptable, unacceptable, insufficient or not found?

    An essay is acceptable if it expicitly contains standalone phrases that exactly describe the concept of {topic_full[topic]} accurately.

    An essay is unacceptable if it contains phrases that are inaccurate about {topic_full[topic]}.

    An essay is insufficient if it contains phrases that may be accurate but cannot fully define the concept of {topic_full[topic]}.

    An essay is not found if it contains no relevant statements about {topic_full[topic]}.

    Write your final decision to the question as one of: "Decision: [ACCEPTABLE]" or "Decision: [UNACCEPTABLE]" or "Decision: [INSUFFICIENT]" or "Decision: [NOT FOUND]". DO NOT fill in your decision with any terms other than ACCEPTABLE or UNACCEPTABLE or INSUFFICIENT or NOT FOUND. Then, finish by providing your reasoning when considering this question starting with "Reasoning:".

    Decision:'''
        return prompt

    # Input:
    # - essays: a list of strings. Each string is a student's essay
    # - topic: a string. Either "PE","KE" or "LCE"
    # Output:
    # - A list of dictionaries, where each dictionary has exactly 2 key-value pairs in the following form.
    # {'essay':'insert student essay here', 'evaluation':'insert classification here'}
    # 1. 'essay': the value is the student's essay
    # 2. 'evaluation': the string that represents the evaluation of that essay. Can be 'acceptable', 'unacceptable',
    # 'insufficient', 'not found', or 'reported other words: xxx'
    # of the model report anything that is unrelated to the task

    def bloom_classification(self, essay, topic):
        # Prepare the prompt
        prompt = self.prepare_prompt(essay, topic)
        # Memorize the length of the prompt
        prompt_len = len(prompt)

        # Get the output from the model
        output = self.bloom_output(prompt, topic)

        # we only cares about the new part of the text, so we ignore the part which is our prompt
        output = output[prompt_len:-1].lower()

        # Extract answer from the response
        answer = []
        if 'unacceptable' in output:
            answer.append('unacceptable')
        elif 'acceptable' in output:
            answer.append('acceptable')
        if 'insufficient' in output:
            answer.append('insufficient')
        if 'not found' in output:
            answer.append('not found')

        # Get final answer
        if len(answer) == 0:
            return f'reported other words: {output}'
        else:
            return answer[0]

    # the following function receives a string, which is a text,
    # and outputs a dictionary
    # The keys in dictionary are "PE", "KE" and "LCE"
    # The values could be "acceptable", "unacceptable", "insufficient", "not found"
    # or "reported other words" if the model does not produce any meaningful labels
    def get_results(self, sample):
        answer = {"PE": self.bloom_classification(sample, "PE"), "KE": self.bloom_classification(sample, "KE"),
                  "LCE": self.bloom_classification(sample, "LCE")}
        return answer


bloom = Bloom()
print(bloom.get_results("Hi"))
