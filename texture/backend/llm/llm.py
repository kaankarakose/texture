from transformers import AutoModelForCausalLM, AutoTokenizer
import time

class QwenModel:
    def __init__(self, model_name="Qwen/Qwen2.5-32B-Instruct", device="cuda:0"):
        self.model_name = model_name
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map=device,
            attn_implementation="flash_attention_2",
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
    def preprocess(self, messages):

        messages = [{"role": message['role'], "content": message["content"]} for message in messages]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        print(f"Text: {text}")
        
        return self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
    def generate(self, messages, temperature, max_new_tokens):
        start = time.time()
        
        model_inputs = self.preprocess(messages)
        
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature
        )
        
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        end = time.time()
        print(f"Time elapsed: {end - start} seconds")
        
        return self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
