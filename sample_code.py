import os

def greet(name):
    print(f"Hello, {name}!")

# Example of reading user input - could be flagged depending on context
user_name = input("Enter your name: ") 
greet(user_name)

# Example potentially flagged issue: using os.system (can be dangerous if input is not sanitized)
# command = input("Enter a command to run: ")
# os.system(command) 

print("Script finished.") 