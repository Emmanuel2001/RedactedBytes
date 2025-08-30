import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from functools import lru_cache

# Load the model and tokenizer
model_name = "iiiorg/piiranha-v1-detect-personal-information"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

@lru_cache(maxsize=1)
def get_model():
    # If you load spaCy/transformers/etc., do it here once.
    # If regex-only, just return a sentinel.
    return "ready"

def predict(text, aggregate_redaction=False):
    _ = get_model()  # ensures one-time init
    # Tokenize input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    # Get model predictions
    with torch.no_grad():
        outputs = model(**inputs)
    # Get predicted labels
    predictions = torch.argmax(outputs.logits, dim=-1)
    # Token offsets for redaction
    encoded_inputs = tokenizer.encode_plus(text, return_offsets_mapping=True, add_special_tokens=True)
    offset_mapping = encoded_inputs['offset_mapping']
    masked_text = list(text)
    is_redacting = False
    redaction_start = 0
    current_pii_type = ''
    for i, (start, end) in enumerate(offset_mapping):
        if start == end:  # Special token
            continue
        label = predictions[0][i].item()
        if label != model.config.label2id['O']:  # PII detected
            pii_type = model.config.id2label[label]
            if not is_redacting:
                is_redacting = True
                redaction_start = start
                current_pii_type = pii_type
            elif not aggregate_redaction and pii_type != current_pii_type:
                # End current redaction and start a new one
                apply_redaction(masked_text, redaction_start, start, current_pii_type, aggregate_redaction)
                redaction_start = start
                current_pii_type = pii_type
        else:
            if is_redacting:
                apply_redaction(masked_text, redaction_start, end, current_pii_type, aggregate_redaction)
                is_redacting = False
    # Handle case where PII is at the end of the text
    if is_redacting:
        apply_redaction(masked_text, redaction_start, len(masked_text), current_pii_type, aggregate_redaction)
    return ''.join(masked_text)

def apply_redaction(masked_text, start, end, pii_type, aggregate_redaction):
    for j in range(start, end):
        masked_text[j] = ''
    if aggregate_redaction:
        masked_text[start] = '[redacted]'
    else:
        masked_text[start] = f'[{pii_type}]'
        
def main():
    example_text = "My name is Dhanushkumar and I live at Chennai. My phone number is +9190803470. My credit card number is 4605170010026518."
    print("Aggregated redaction:")
    masked_example_aggregated = predict(example_text, aggregate_redaction=True)
    print(masked_example_aggregated)
    print("\nDetailed redaction:")
    masked_example_detailed = predict(example_text, aggregate_redaction=False)
    print(masked_example_detailed)

# Example usage
if __name__ == "__main__":
    main()