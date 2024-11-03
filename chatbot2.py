# -*- coding: utf-8 -*-
"""chatbot2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1thRcc8vxMQ0lD8NLbwrtQmfduw2Q3kWl
"""

pip install transformers torch gradio

!pip install multipart

!pip show multipart

!pip uninstall multipart -y
!pip install multipart

!pip install --upgrade gradio transformers

!pip uninstall multipart gradio -y

!pip install gradio

!pip show multipart
!pip show gradio

import gradio as gr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments
import torch

# Load model directly
tokenizer = AutoTokenizer.from_pretrained("Tianlin668/MentalBART")
model = AutoModelForSeq2SeqLM.from_pretrained("Tianlin668/MentalBART")

# Example training data
train_data = [
    {"input": "What should I do if I'm feeling anxious?", "output": "It's important to talk to someone. Consider reaching out to a friend or a mental health professional."},
    {"input": "How can I manage stress better?", "output": "Practicing mindfulness and deep-breathing exercises can be very helpful. Additionally, regular physical activity can reduce stress."},
    {"input": "What are some signs of depression?", "output": "Signs of depression can include persistent sadness, loss of interest in activities, changes in appetite, and difficulty sleeping."},
    {"input": "I feel overwhelmed with everything going on. What can I do?", "output": "Take a step back and prioritize your tasks. Break them into smaller, manageable steps, and don't hesitate to ask for help."},
    {"input": "How can I help a friend who seems depressed?", "output": "Be there for them and listen without judgment. Encourage them to seek professional help if needed."},
    {"input": "What if I'm not comfortable talking to someone?", "output": "It's okay to feel that way. You can start by writing down your feelings or expressing them through art."},
    {"input": "Can you tell me about cognitive behavioral therapy?", "output": "Cognitive Behavioral Therapy (CBT) is a type of therapy that helps people identify and change negative thought patterns and behaviors."},
    {"input": "I keep having negative thoughts. What should I do?", "output": "Try to challenge those thoughts by identifying evidence that contradicts them. Writing them down can also help you see them more clearly."},
    {"input": "What should I do if I feel like I have no one to talk to?", "output": "Consider contacting a helpline or support group. There are people who care and want to help."},
    {"input": "I'm feeling fine, but I have some questions. Can you help?", "output": "Of course! Feel free to ask anything, and I'll do my best to provide the information you're looking for."},
    # Added guidance questions
    {"input": "Can you give me step-by-step instructions on how to meditate?", "output": "1. Find a quiet place. 2. Sit comfortably. 3. Close your eyes. 4. Focus on your breath. 5. If your mind wanders, gently bring it back to your breath."},
    {"input": "What are some tips for a healthy sleep routine?", "output": "1. Set a consistent sleep schedule. 2. Create a calming bedtime routine. 3. Limit screen time before bed. 4. Keep your bedroom dark and cool."},
    {"input": "How can I stay motivated to exercise regularly?", "output": "Set specific goals, schedule workouts like appointments, and find a workout buddy to keep you accountable."},
    # Added error handling responses
    {"input": "", "output": "I'm sorry, I didn't catch that. Could you please ask something else?"},
    {"input": "How can I help with world hunger?", "output": "That's a great question! However, I focus on mental health topics. For such inquiries, consider reaching out to relevant organizations or experts."},
    {"input": "Can you tell me how to invest in stocks?", "output": "I'm here to discuss mental health. For investing advice, you might want to consult a financial advisor."},
    {"input": "What are the latest news on climate change?", "output": "I focus on mental health support. You can check news websites for the latest updates on climate change."},

]

# Tokenize the data
inputs = tokenizer([item["input"] for item in train_data], return_tensors="pt", padding=True, truncation=True)
outputs = tokenizer([item["output"] for item in train_data], return_tensors="pt", padding=True, truncation=True)

# Create a dataset object
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = self.labels['input_ids'][idx]
        return item

    def __len__(self):
        return len(self.labels['input_ids'])

# Create dataset
dataset = CustomDataset(inputs, outputs)

# Set training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=10_000,
    save_total_limit=2,
)

# Create Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

# Fine-tune the model
trainer.train()

# Define the inference function
def inference(prompt):
    if not prompt or prompt.strip() == "":
        return "I'm sorry, I didn't catch that. Could you please ask something else?"

    input_ids = tokenizer.encode(prompt, return_tensors="pt")

    try:
        output = model.generate(input_ids, max_length=150, num_beams=5, early_stopping=True)
        result = tokenizer.decode(output[0], skip_special_tokens=True)
    except Exception as e:
        result = "Sorry, I encountered an error while processing your request."

    return result

with gr.Blocks() as demo:
    gr.Markdown("<center><h1>This is your virtual assistant - MentalBART model</h1></center>")
    gr.Markdown("<center><h2>This assistant will try to diagnose for depression and provide reasoning for it.</h2></center>")

    # Input boxes for the prompt
    prompt = gr.Textbox(label="Prompt", lines=3, max_lines=5)

    # Button for generating response
    generate_btn = gr.Button("Generate Response")
    output = gr.Markdown("Response will appear here.")

    # Trigger the inference function on button click
    generate_btn.click(fn=inference, inputs=[prompt], outputs=[output])

if __name__ == "__main__":
    demo.launch()