import aiml
import os

# Create AIML Kernel
kernel = aiml.Kernel()

# Load AIML file
if os.path.exists("symptoms.aiml"):
    kernel.learn("symptoms.aiml")
else:
    print("symptoms.aiml not found!")

print("🤖 Symptom Bot (AIML) – type 'quit' to exit")

# Chat loop
while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "quit":
        break
    response = kernel.respond(user_input.upper())
    print("Bot:", response)
