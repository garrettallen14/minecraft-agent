import torch
from transformers import BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

# Get our initial top k tokens
def get_topk_tokens(model, inputs, num_branches=10):
        
    # Generate logits for the next token after the prompt 
    with torch.no_grad():
        outputs = model(**inputs, return_dict=True)
        next_token_logits = outputs.logits[:, -1, :]
    
    # Apply softmax to convert logits to probabilities
    probabilities = torch.softmax(next_token_logits, dim=-1)

    # Get the top k tokens and their probabilities
    topk_values, topk_indicies = torch.topk(probabilities, num_branches)

    return topk_values, topk_indicies


# Generate a full response from the model and log the difference in probabilities between the top two tokens
def generate_response(model, tokenizer, inputs, max_length=500):

    # Create variables to store our response and each token's probabilities
    response = []
    response_probs = []
    # Loop through the max length of the response
    for i in range(max_length):

        # Generate the logits for the next token
        topk_values, topk_indices = get_topk_tokens(model, inputs, num_branches=2)

        # Get the difference in probabilities between the top two tokens
        prob_diff = topk_values[:, 0] - topk_values[:, 1]
        response_probs.append(prob_diff.item())

        # Append the most likely token to the response
        response.append(topk_indices[:, 0])

        # Stop if this token is the end of sequence token
        if topk_indices[:, 0] == tokenizer.eos_token_id:
            break

        # Add the token to the input for the next iteration
        inputs['input_ids'] = torch.cat([inputs['input_ids'], topk_indices[:, 0].unsqueeze(-1)], dim=1)

    return inputs['input_ids'], response_probs

# Generate all branching responses
def generate_branching_responses(model, tokenizer, prompt, num_branches=10, max_length=500):

    # First we tokenize the prompt
    inputs = tokenizer(prompt, return_tensors="pt")

    # Get our initial top k tokens
    _, topk_indices = get_topk_tokens(model, inputs, num_branches)

    # Create a list to store our responses and each token's probabilities
    responses = []
    response_probs = []
    for k in tqdm(range(num_branches)):

        # Add the kth most likely token to this new branch
        new_input_ids = inputs.copy()
        new_input_ids['input_ids'] = torch.cat([inputs['input_ids'], topk_indices[:, k].unsqueeze(-1)], dim=1)

        # Generate a response and log the difference in probabilities between the top two tokens
        response, probs = generate_response(model, tokenizer, new_input_ids, max_length)

        # Append the response to our list
        responses.append(tokenizer.batch_decode(response))

        # Determine the average difference in probabilities for this response
        response_probs.append(sum(probs) / len(probs))

    return responses, response_probs


def print_responses(responses, response_probs, input_text):
    for i, (response, prob) in enumerate(zip(responses, response_probs)):
        print(f"Response {i+1} (Avg. Confidence: {prob:.4f}): {response[0].split(input_text)[1]}\n")