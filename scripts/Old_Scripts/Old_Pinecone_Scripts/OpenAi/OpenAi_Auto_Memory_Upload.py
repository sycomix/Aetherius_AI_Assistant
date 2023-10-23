import sys
sys.path.insert(0, './scripts')
sys.path.insert(0, './config')
sys.path.insert(0, './config/Chatbot_Prompts')
sys.path.insert(0, './scripts/resources')
import os
import openai
import json
import time
from time import time, sleep
import datetime
from uuid import uuid4
import pinecone
import importlib.util
from basic_functions import *
import multiprocessing
import threading
import concurrent.futures
import customtkinter
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, font
# import speech_recognition as sr
# from gtts import gTTS
# from playsound import playsound
# import pyttsx3
# from pydub import AudioSegment
# from pydub.playback import play
# from pydub import effects


def load_conversation_explicit_short_term_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = []
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/explicit_short_term_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()
    
    
def load_conversation_explicit_long_term_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = []
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/explicit_long_term_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()
    
    
def load_conversation_episodic_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = []
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/episodic_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()  
    
    
def load_conversation_flashbulb_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = []
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/flashbulb_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip() 
    
    
def load_conversation_heuristics(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = []
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/heuristics_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()    


def load_conversation_implicit_short_term_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = []
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/implicit_short_term_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()  
    
    
def load_conversation_cadence(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = []
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/cadence_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip() 
    
    
def load_conversation_implicit_long_term_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = []
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/implicit_long_term_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()
    
def timeout_check():
    try:
        pinecone.init(api_key=open_file('api_keys/key_pinecone.txt'), environment=open_file('api_keys/key_pinecone_env.txt'))
        return pinecone.Index("aetherius")
    except pinecone.exceptions.PineconeException as e:
        if "timed out" not in str(e):
            raise e
        print("Connection timed out. Reconnecting...")
        timeout_check()

openai.api_key = open_file('api_keys/key_openai.txt')


pinecone.init(api_key=open_file('api_keys/key_pinecone.txt'), environment=open_file('api_keys/key_pinecone_env.txt'))
vdb = pinecone.Index("aetherius")


# Import GPT Calls based on set Config
def import_functions_from_script(script_path):
    spec = importlib.util.spec_from_file_location("custom_module", script_path)
    custom_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(custom_module)
    globals().update(vars(custom_module))
def get_script_path_from_file(file_path):
    with open(file_path, 'r') as file:
        script_name = file.read().strip()
    return f'./scripts/resources/{script_name}.py'
# Define the paths to the text file and scripts directory
file_path = './config/model.txt'
# Read the script name from the text file
script_path = get_script_path_from_file(file_path)
# Import the functions from the desired script
import_functions_from_script(script_path)


# Set the Theme for the Chatbot
def set_dark_ancient_theme():
    background_color = "#2B303A"  # Dark blue-gray
    foreground_color = "#FDF7E3"  # Pale yellow
    button_color = "#415A77"  # Dark grayish blue
    text_color = 'white'

    return background_color, foreground_color, button_color, text_color
    
    
# Function for Uploading Cadence, called in the create widgets function.
def DB_Upload_Cadence(query):
    # key = input("Enter OpenAi API KEY:")
    vdb = pinecone.Index("aetherius")
    index_info = vdb.describe_index_stats()
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    print('Pinecone DB Info')
    print(index_info)
    print("Type [Delete All Data] to delete saved Cadence.")
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    if not os.path.exists(f'nexus/{bot_name}/{username}/cadence_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/cadence_nexus')
    while True:
     #   a = input(f'\n\nUSER: ')
        if query == 'Delete All Data':
            while True:
                print('\n\nSYSTEM: Are you sure you would like to delete the saved Cadence?\n        Press Y for yes or N for no.')
                user_input = input("'Y' or 'N': ")
                if user_input == 'y':
                    vdb.delete(filter={"memory_type": "cadence", "user": username}, namespace=f'{bot_name}')
                    while True:
                        print('All saved cadence has been Deleted')
                        return
                elif user_input == 'n':
                    print('\n\nSYSTEM: Cadence delete cancelled.')
                    return
        if query == 'Exit':
            while True:
                return
        vector = gpt3_embedding(query)
        timestamp = time()
        timestring = timestamp_to_datetime(timestamp)
        unique_id = str(uuid4())
        metadata = {'speaker': bot_name, 'time': timestamp, 'message': query, 'timestring': timestring,
                    'uuid': unique_id, "memory_type": "cadence", "user": username}
        save_json(f'nexus/{bot_name}/{username}/cadence_nexus/%s.json' % unique_id, metadata)
        payload = [(unique_id, vector, {"memory_type": "cadence", "user": username})]
        vdb.upsert(payload, namespace=f'{bot_name}')
        print('\n\nSYSTEM: Upload Successful!')
        return query
        
        
# Function for Uploading Heuristics, called in the create widgets function.
def DB_Upload_Heuristics(query):
    # key = input("Enter OpenAi API KEY:")
    vdb = pinecone.Index("aetherius")
    index_info = vdb.describe_index_stats()
    print('Pinecone DB Info')
    print(index_info)
    print("Type [Delete All Data] to delete saved Heuristics.")
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    if not os.path.exists(f'nexus/{bot_name}/{username}/heuristics_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/heuristics_nexus')
    while True:
    #    a = input(f'\n\nUSER: ')
        if query == 'Delete All Data':
            while True:
                print('\n\nSYSTEM: Are you sure you would like to delete the saved Heuristics?\n        Press Y for yes or N for no.')
                user_input = input("'Y' or 'N': ")
                if user_input == 'y':
                    vdb.delete(filter={"memory_type": "heuristics", "user": username}, namespace=f'{bot_name}')
                    while True:
                        print('All heuristics have been Deleted')
                        return
                elif user_input == 'n':
                    print('\n\nSYSTEM: Heuristics delete cancelled.')
                    return
        if query == 'Exit':
            while True:
                return
        vector = gpt3_embedding(query)
        timestamp = time()
        timestring = timestamp_to_datetime(timestamp)
        unique_id = str(uuid4())
        metadata = {'speaker': bot_name, 'time': timestamp, 'message': query, 'timestring': timestring,
                    'uuid': unique_id, "memory_type": "heuristics", "user": username}
        save_json(f'nexus/{bot_name}/{username}/heuristics_nexus/%s.json' % unique_id, metadata)
        payload = [
            (
                unique_id,
                vector,
                {"memory_type": "heuristics", "user": username},
            )
        ]
        vdb.upsert(payload, namespace=f'{bot_name}')
        print('\n\nSYSTEM: Upload Successful!')
        return query
        
        
# Running Conversation List
class MainConversation:
    def __init__(self, max_entries, prompt, greeting):
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        self.max_entries = max_entries
        self.file_path = f'./history/{username}/{bot_name}_main_conversation_history.json'
        self.main_conversation = [prompt, greeting]

        # Load existing conversation from file
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.running_conversation = data.get('running_conversation', [])
        else:
            self.running_conversation = []

    def append(self, timestring, username, a, bot_name, output_one, output_two, response_two):
        # Append new entry to the running conversation
        entry = [
            f"{timestring}-{username}: {a}",
            f"{bot_name}'s Inner Monologue: {output_one}",
            f"Intuition: {output_two}",
            f"Response: {response_two}",
        ]
        self.running_conversation.append("\n\n".join(entry))  # Join the entry with "\n\n"

        # Remove oldest entry if conversation length exceeds max entries
        while len(self.running_conversation) > self.max_entries:
            self.running_conversation.pop(0)
        self.save_to_file()

    def save_to_file(self):
        # Combine main conversation and formatted running conversation for saving to file
        data_to_save = {
            'main_conversation': self.main_conversation,
            'running_conversation': self.running_conversation
        }
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)

    def get_conversation_history(self):
        return self.main_conversation + ["\n\n".join(entry.split("\n\n")) for entry in self.running_conversation]
        
    
class ChatBotApplication(tk.Frame):
    # Create Tkinter GUI
    def __init__(self, master=None):
        super().__init__(master)
        (
            self.background_color,
            self.foreground_color,
            self.button_color,
            self.text_color
        ) = set_dark_ancient_theme()

        self.master = master
        self.master.configure(bg=self.background_color)
        self.master.title('Aetherius Chatbot')
        self.pack(fill="both", expand=True)
        self.create_widgets()
        # Load and display conversation history
        self.display_conversation_history()
        
    
    def bind_enter_key(self):
        self.user_input.bind("<Return>", lambda event: self.send_message())
        
        
    def copy_selected_text(self):
        selected_text = self.conversation_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        self.clipboard_clear()
        self.clipboard_append(selected_text)
        
        
    def show_context_menu(self, event):
        # Create the menu
        menu = tk.Menu(self, tearoff=0)
        # Right Click Menu
        menu.add_command(label="Copy", command=self.copy_selected_text)
        # Display the menu at the clicked position
        menu.post(event.x_root, event.y_root)
        
        
    def display_conversation_history(self):
        # Load the conversation history from the JSON file
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        file_path = f'./history/{username}/{bot_name}_main_conversation_history.json'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
            # Retrieve the conversation history
            conversation_history = conversation_data['main_conversation'] + conversation_data['running_conversation']
            # Display the conversation history in the text widget
            for entry in conversation_history:
                message = '\n'.join(entry) if isinstance(entry, list) else entry
                self.conversation_text.insert(tk.END, message + '\n\n')
        except FileNotFoundError:
            # Handle the case when the JSON file is not found
            greeting_msg = open_file('./config/Chatbot_Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
            self.conversation_text.insert(tk.END, greeting_msg + '\n\n')
        self.conversation_text.yview(tk.END)
        
    
    # Edit Bot Name
    def choose_bot_name(self):
        if bot_name := simpledialog.askstring(
            "Choose Bot Name", "Type a Bot Name:"
        ):
            file_path = "./config/prompt_bot_name.txt"
            with open(file_path, 'w') as file:
                file.write(bot_name)
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()  
        

    # Edit User Name
    def choose_username(self):
        if username := simpledialog.askstring(
            "Choose Username", "Type a Username:"
        ):
            file_path = "./config/prompt_username.txt"
            with open(file_path, 'w') as file:
                file.write(username)
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()
        
        
    # Edits Main Chatbot System Prompt
    def Edit_Main_Prompt(self):
        file_path = "./config/Chatbot_Prompts/prompt_main.txt"

        with open(file_path, 'r') as file:
            prompt_contents = file.read()

        top = tk.Toplevel(self)
        top.title("Edit Main Prompt")

        prompt_text = tk.Text(top, height=10, width=60)
        prompt_text.insert(tk.END, prompt_contents)
        prompt_text.pack()


        def save_prompt():
            new_prompt = prompt_text.get("1.0", tk.END).strip()
            with open(file_path, 'w') as file:
                file.write(new_prompt)
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()

        save_button = tk.Button(top, text="Save", command=save_prompt)
        save_button.pack()
        
        
    # Edit secondary prompt (Less priority than main prompt)    
    def Edit_Secondary_Prompt(self):
        file_path = "./config/Chatbot_Prompts/prompt_secondary.txt"
        
        with open(file_path, 'r') as file:
            prompt_contents = file.read()
        
        top = tk.Toplevel(self)
        top.title("Edit Secondary Prompt")
        
        prompt_text = tk.Text(top, height=10, width=60)
        prompt_text.insert(tk.END, prompt_contents)
        prompt_text.pack()
        
        def save_prompt():
            new_prompt = prompt_text.get("1.0", tk.END).strip()
            with open(file_path, 'w') as file:
                file.write(new_prompt)
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()
        
        save_button = tk.Button(top, text="Save", command=save_prompt)
        save_button.pack()
        
       
    # Change Font Style, called in create widgets
    def Edit_Font(self):
        file_path = "./config/font.txt"

        with open(file_path, 'r') as file:
            font_value = file.read()

        fonts = font.families()

        top = tk.Toplevel(self)
        top.title("Edit Font")

        font_listbox = tk.Listbox(top)
        font_listbox.pack()
        for font_name in fonts:
            font_listbox.insert(tk.END, font_name)
            
        label = tk.Label(top, text="Enter the Font Name:")
        label.pack()

        font_entry = tk.Entry(top)
        font_entry.insert(tk.END, font_value)
        font_entry.pack()

        def save_font():
            new_font = font_entry.get()
            if new_font in fonts:
                with open(file_path, 'w') as file:
                    file.write(new_font)
                self.update_font_settings()
            top.destroy()
            
        save_button = tk.Button(top, text="Save", command=save_font)
        save_button.pack()
        

    # Change Font Size, called in create widgets
    def Edit_Font_Size(self):
        file_path = "./config/font_size.txt"

        with open(file_path, 'r') as file:
            font_size_value = file.read()

        top = tk.Toplevel(self)
        top.title("Edit Font Size")

        label = tk.Label(top, text="Enter the Font Size:")
        label.pack()

        self.font_size_entry = tk.Entry(top)
        self.font_size_entry.insert(tk.END, font_size_value)
        self.font_size_entry.pack()

        def save_font_size():
            new_font_size = self.font_size_entry.get()
            if new_font_size.isdigit():
                with open(file_path, 'w') as file:
                    file.write(new_font_size)
                self.update_font_settings()
            top.destroy()

        save_button = tk.Button(top, text="Save", command=save_font_size)
        save_button.pack()

        top.mainloop()
        

    #Fallback to size 10 if no font size
    def update_font_settings(self):
        font_config = open_file('./config/font.txt')
        font_size = open_file('./config/font_size.txt')
        try:
            font_size_config = int(font_size)
        except:
            font_size_config = 10
        font_style = (f"{font_config}", font_size_config)

        self.conversation_text.configure(font=font_style)
        self.user_input.configure(font=(f"{font_config}", 10))
        
        
    # Edits initial chatbot greeting, called in create widgets
    def Edit_Greeting_Prompt(self):
        file_path = "./config/Chatbot_Prompts/prompt_greeting.txt"
        
        with open(file_path, 'r') as file:
            prompt_contents = file.read()
        
        top = tk.Toplevel(self)
        top.title("Edit Greeting Prompt")
        
        prompt_text = tk.Text(top, height=10, width=60)
        prompt_text.insert(tk.END, prompt_contents)
        prompt_text.pack()
        
        def save_prompt():
            new_prompt = prompt_text.get("1.0", tk.END).strip()
            with open(file_path, 'w') as file:
                file.write(new_prompt)
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()
        
        save_button = tk.Button(top, text="Save", command=save_prompt)
        save_button.pack()
        
        
    # Edits running conversation list
    def Edit_Conversation(self):
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        file_path = f"./history/{username}/{bot_name}_main_conversation_history.json"

        with open(file_path, 'r') as file:
            conversation_data = json.load(file)

        running_conversation = conversation_data.get("running_conversation", [])

        top = tk.Toplevel(self)
        top.title("Edit Running Conversation")

        entry_texts = []  # List to store the entry text widgets

        def update_entry():
            nonlocal entry_index
            entry_text.delete("1.0", tk.END)
            entry_text.insert(tk.END, running_conversation[entry_index].strip())
            entry_number_label.config(text=f"Entry {entry_index + 1}/{len(running_conversation)}")

        entry_index = 0

        entry_text = tk.Text(top, height=10, width=60)
        entry_text.pack(fill=tk.BOTH, expand=True)
        entry_texts.append(entry_text)  # Store the reference to the entry text widget

        entry_number_label = tk.Label(top, text=f"Entry {entry_index + 1}/{len(running_conversation)}")
        entry_number_label.pack()

        update_entry()

        def go_back():
            nonlocal entry_index
            if entry_index > 0:
                entry_index -= 1
                update_entry()

        def go_forward():
            nonlocal entry_index
            if entry_index < len(running_conversation) - 1:
                entry_index += 1
                update_entry()

        back_button = tk.Button(top, text="Back", command=go_back)
        back_button.pack(side=tk.LEFT)

        forward_button = tk.Button(top, text="Forward", command=go_forward)
        forward_button.pack(side=tk.LEFT)

        def save_conversation():
            for i, entry_text in enumerate(entry_texts):
                entry_lines = entry_text.get("1.0", tk.END).strip()  # Remove leading/trailing whitespace
                running_conversation[entry_index + i] = entry_lines

            conversation_data["running_conversation"] = running_conversation

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(conversation_data, file, indent=4, ensure_ascii=False)

            # Update your conversation display or perform any required actions here
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()
            update_entry()  # Update the displayed entry in the cycling menu

        save_button = tk.Button(top, text="Save", command=save_conversation)
        save_button.pack()

        # Configure the top level window to scale with the content
        top.pack_propagate(False)
        top.geometry("600x400")  # Set the initial size of the window
        
        
    # Selects which Open Ai model to use.    
    def Model_Selection(self):
        file_path = "./config/model.txt"
        
        with open(file_path, 'r') as file:
            prompt_contents = file.read()
        
        top = tk.Toplevel(self)
        top.title("Select a Model")
        
        models_label = tk.Label(top, text="Available Models: gpt_35, gpt_35_16, gpt_4")
        models_label.pack()
        
        prompt_text = tk.Text(top, height=10, width=60)
        prompt_text.insert(tk.END, prompt_contents)
        prompt_text.pack()
        
        def save_prompt():
            new_prompt = prompt_text.get("1.0", tk.END).strip()
            with open(file_path, 'w') as file:
                file.write(new_prompt)
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()
        
        save_button = tk.Button(top, text="Save", command=save_prompt)
        save_button.pack()
        
        
    def update_results(self, text_widget, search_results):
        self.after(0, text_widget.delete, "1.0", tk.END)
        self.after(0, text_widget.insert, tk.END, search_results)
        
        
        
    def open_cadence_window(self):
        cadence_window = tk.Toplevel(self)
        cadence_window.title("Cadence DB Upload")

        query_label = tk.Label(cadence_window, text="Enter Cadence Example:")
        query_label.pack()

        query_entry = tk.Entry(cadence_window)
        query_entry.pack()

        results_label = tk.Label(cadence_window, text="Scrape results: ")
        results_label.pack()

        results_text = tk.Text(cadence_window)
        results_text.pack()

        def perform_search():
            query = query_entry.get()

            def update_results():
                # Update the GUI with the new paragraph
                self.results_text.insert(tk.END, f"{query}\n\n")
                self.results_text.yview(tk.END)

            def search_task():
                # Call the modified GPT_3_5_Tasklist_Web_Search function with the callback
                search_results = DB_Upload_Cadence(query)
                self.update_results(results_text, search_results)

            t = threading.Thread(target=search_task)
            t.start()

        search_button = tk.Button(cadence_window, text="Upload", command=perform_search)
        search_button.pack()
        
        
        
    def open_heuristics_window(self):
        heuristics_window = tk.Toplevel(self)
        heuristics_window.title("Heuristics DB Upload")

        query_label = tk.Label(heuristics_window, text="Enter Heuristics:")
        query_label.pack()

        query_entry = tk.Entry(heuristics_window)
        query_entry.pack()

        results_label = tk.Label(heuristics_window, text="Entered Heuristics: ")
        results_label.pack()

        results_text = tk.Text(heuristics_window)
        results_text.pack()

        def perform_search():
            query = query_entry.get()

            def update_results(query):
                # Update the GUI with the new paragraph
                results_text.insert(tk.END, f"{query}\n\n")
                results_text.yview(tk.END)

            def search_task():
                # Call the modified GPT_3_5_Tasklist_Web_Search function with the callback
                search_results = DB_Upload_Heuristics(query)

                # Use the `after` method to schedule the `update_results` function on the main Tkinter thread
                heuristics_window.after(0, update_results, search_results)

            t = threading.Thread(target=search_task)
            t.start()

        search_button = tk.Button(heuristics_window, text="Upload", command=perform_search)
        search_button.pack()
    
        
    def handle_menu_selection(self, event):
        selection = self.menu.get()
        if selection == "Edit Main Prompt":
            self.Edit_Main_Prompt()
        elif selection == "Edit Secondary Prompt":
            self.Edit_Secondary_Prompt()
        elif selection == "Edit Greeting Prompt":
            self.Edit_Greeting_Prompt()
        elif selection == "Edit Font":
            self.Edit_Font()
        elif selection == "Edit Font Size":
            self.Edit_Font_Size()
        elif selection == "Model Selection":
            self.Model_Selection()
            
            
    def handle_login_menu_selection(self, event):
        selection = self.login_menu.get()
        if selection == "Choose Bot Name":
            self.choose_bot_name()
        elif selection == "Choose Username":
            self.choose_username()
            
            
    def handle_db_menu_selection(self, event):
        selection = self.db_menu.get()
        if selection == "Cadence DB Upload":
            self.open_cadence_window()
        elif selection == "Heuristics DB Upload":
            self.open_heuristics_window()

        
    def create_widgets(self):
        font_config = open_file('./config/font.txt')
        font_size = open_file('./config/font_size.txt')
        try:
            font_size_config = int(font_size)
        except:
            font_size_config = 10
        font_style = (f"{font_config}", font_size_config)
        
        self.top_frame = tk.Frame(self, bg=self.background_color)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.placeholder_label = tk.Label(self.top_frame, bg=self.background_color)
        self.placeholder_label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Login dropdown Menu
        self.login_menu = ttk.Combobox(self.top_frame, values=["Login Menu", "----------------------------", "Choose Bot Name", "Choose Username"], state="readonly")
        self.login_menu.pack(side=tk.LEFT, padx=5, pady=5)
        self.login_menu.current(0)
        self.login_menu.bind("<<ComboboxSelected>>", self.handle_login_menu_selection)
        
        # Edit Conversation Button
        self.update_history_button = tk.Button(self.top_frame, text="Edit Conversation", command=self.Edit_Conversation, bg=self.button_color, fg=self.text_color)
        self.update_history_button.pack(side=tk.LEFT, padx=5, pady=5, ipadx=10)
        
        # DB Management Dropdown menu
        self.db_menu = ttk.Combobox(self.top_frame, values=["DB Management", "----------------------------", "Cadence DB Upload", "Heuristics DB Upload"], state="readonly")
        self.db_menu.pack(side=tk.LEFT, padx=5, pady=5)
        self.db_menu.current(0)
        self.db_menu.bind("<<ComboboxSelected>>", self.handle_db_menu_selection)
        
        # Delete Conversation Button
        self.delete_history_button = tk.Button(self.top_frame, text="Clear Conversation", command=self.delete_conversation_history, bg=self.button_color, fg=self.text_color)
        self.delete_history_button.pack(side=tk.LEFT, padx=5, pady=5, ipadx=10)
        
        # Config Dropdown Menu
        self.menu = ttk.Combobox(self.top_frame, values=["Config Menu", "----------------------------", "Model Selection", "Edit Font", "Edit Font Size", "Edit Main Prompt", "Edit Secondary Prompt", "Edit Greeting Prompt"], state="readonly")
        self.menu.pack(side=tk.LEFT, padx=5, pady=5)
        self.menu.current(0)
        self.menu.bind("<<ComboboxSelected>>", self.handle_menu_selection)
        

        self.placeholder_label = tk.Label(self.top_frame, bg=self.background_color)
        self.placeholder_label.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # Enables wordwrap and disables input when chatbot is thinking.
        self.conversation_text = tk.Text(self, bg=self.background_color, fg=self.text_color, wrap=tk.WORD)
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        self.conversation_text.configure(font=font_style)
        self.conversation_text.bind("<Key>", lambda e: "break")  # Disable keyboard input
        self.conversation_text.bind("<Button>", lambda e: "break")  # Disable mouse input

        self.input_frame = tk.Frame(self, bg=self.background_color)
        self.input_frame.pack(fill=tk.X, side="bottom")

        self.user_input = tk.Entry(self.input_frame, bg=self.background_color, fg=self.text_color)
        self.user_input.configure(font=(f"{font_config}", 10))
        self.user_input.pack(fill=tk.X, expand=True, side="left")
        
        self.thinking_label = tk.Label(self.input_frame, text="Thinking...")

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, bg=self.button_color, fg=self.text_color)
        self.send_button.pack(side="right")

        self.grid_columnconfigure(0, weight=1)
        
        self.bind_enter_key()
        self.conversation_text.bind("<1>", lambda event: self.conversation_text.focus_set())
        self.conversation_text.bind("<Button-3>", self.show_context_menu)


    def delete_conversation_history(self):
        # Delete the conversation history JSON file
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        file_path = f'./history/{username}/{bot_name}_main_conversation_history.json'
        try:
            os.remove(file_path)
            # Reload the script
            self.master.destroy()
            OpenAi_Auto_Memory_Upload()
        except FileNotFoundError:
            pass


    def send_message(self):
        a = self.user_input.get()
        self.user_input.delete(0, tk.END)
        self.user_input.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.user_input.unbind("<Return>")
        # Display "Thinking..." in the input field
        self.thinking_label.pack()
        t = threading.Thread(target=self.process_message, args=(a,))
        t.start()


    def process_message(self, a):
        self.conversation_text.insert(tk.END, f"\nYou: {a}\n\n")
        self.conversation_text.yview(tk.END)
        t = threading.Thread(target=self.GPT_Inner_Monologue, args=(a,))
        t.start()
        
        
    def GPT_Inner_Monologue(self, a):
        vdb = pinecone.Index("aetherius")
        # # Number of Messages before conversation is summarized, higher number, higher api cost. Change to 3 when using GPT 3.5 due to token usage.
        m = multiprocessing.Manager()
        lock = m.Lock()
        tasklist = []
        conversation = []
        int_conversation = []
        conversation2 = []
        summary = []
        auto = []
        payload = []
        consolidation = []
        counter = 0
        counter2 = 0
        mem_counter = 0
        length_config = open_file('./config/Conversation_Length.txt')
        conv_length = int(length_config)
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        main_prompt = open_file('./config/Chatbot_Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file('./config/Chatbot_Prompts/prompt_secondary.txt')
        greeting_msg = open_file('./config/Chatbot_Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
        main_conversation = MainConversation(conv_length, main_prompt, greeting_msg)
        if not os.path.exists(f'nexus/{bot_name}/{username}/implicit_short_term_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/implicit_short_term_memory_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/explicit_short_term_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/explicit_short_term_memory_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/explicit_long_term_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/explicit_long_term_memory_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/implicit_long_term_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/implicit_long_term_memory_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/episodic_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/episodic_memory_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/flashbulb_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/flashbulb_memory_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/heuristics_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/heuristics_nexus')
        if not os.path.exists('nexus/global_heuristics_nexus'):
            os.makedirs('nexus/global_heuristics_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/cadence_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/cadence_nexus')
        if not os.path.exists(f'logs/{bot_name}/{username}/complete_chat_logs'):
            os.makedirs(f'logs/{bot_name}/{username}/complete_chat_logs')
        if not os.path.exists(f'logs/{bot_name}/{username}/final_response_logs'):
            os.makedirs(f'logs/{bot_name}/{username}/final_response_logs')
        if not os.path.exists(f'logs/{bot_name}/{username}/inner_monologue_logs'):
            os.makedirs(f'logs/{bot_name}/{username}/inner_monologue_logs')
        if not os.path.exists(f'logs/{bot_name}/{username}/intuition_logs'):
            os.makedirs(f'logs/{bot_name}/{username}/intuition_logs')
        if not os.path.exists(f'history/{username}'):
            os.makedirs(f'history/{username}')
        tasklist_counter = 0
    #   r = sr.Recognizer()
        while True:
            conversation_history = main_conversation.get_conversation_history()
            # # Get Timestamp
            vdb = timeout_check()
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            # # Start or Continue Conversation based on if response exists
            conversation.append({'role': 'system', 'content': f'{main_prompt}'})
            int_conversation.append({'role': 'system', 'content': f'{main_prompt}'})
            if 'response_two' in locals():
                conversation.extend(
                    (
                        {'role': 'user', 'content': a},
                        {'role': 'assistant', 'content': f"{response_two}"},
                    )
                )
            else:
                conversation.append({'role': 'assistant', 'content': f"{greeting_msg}"})
                print("\n%s" % greeting_msg)
            # # User Input Voice
        #    yn_voice = input(f'\n\nPress Enter to Speak')
        #    if yn_voice == "":
        #        with sr.Microphone() as source:
        #            print("\nSpeak now")
        #            audio = r.listen(source)
        #            try:
        #                text = r.recognize_google(audio)
        #                print("\nUSER: " + text)
        #            except sr.UnknownValueError:
        #                print("Google Speech Recognition could not understand audio")
        #                print("\nSYSTEM: Press Left Alt to Speak to Aetherius")
        #                break
        #            except sr.RequestError as e:
        #                print("Could not request results from Google Speech Recognition service; {0}".format(e))
        #                break
        #    else:
        #        print('Leave Field Empty')
        #    a = (f'\n\nUSER: {text}')
            # # User Input Text
   #         a = input(f'\n\nUSER: ')
            message_input = a
            vector_input = gpt3_embedding(message_input)
            # # Check for Commands
            # # Check for "Clear Memory"
            if a == 'Clear Memory':
                while True:
                    print('\n\nSYSTEM: Are you sure you would like to delete saved short-term memory?\n        Press Y for yes or N for no.')
                    user_input = input("'Y' or 'N': ")
                    if user_input == 'y':
                        vdb.delete(delete_all=True, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                        file_path = f'./history/{username}/{bot_name}_main_conversation_history.json'
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        print('Short-Term Memory has been Deleted')
                        return
                    elif user_input == 'n':
                        print('\n\nSYSTEM: Short-Term Memory delete cancelled.')
                        return
            # # Check for "Exit"
            if a == 'Exit':
                return
            conversation.append({'role': 'user', 'content': a})
            tasklist.extend(
                (
                    {
                        'role': 'system',
                        'content': "You are a task coordinator. Your job is to take user input and create a list of 2-5 inquiries to be used for a semantic database search of a chatbot's memories. Use the format [- 'INQUIRY'].",
                    },
                    {'role': 'user', 'content': f"USER INQUIRY: {a}"},
                    {
                        'role': 'assistant',
                        'content': "List of Semantic Search Terms: ",
                    },
                )
            )
            tasklist_output = chatgpt200_completion(tasklist)
            lines = tasklist_output.splitlines()
            db_term = {}
            db_term_result = {}
            db_term_result2 = {}
            # # Split bullet points into separate lines to be used as individual queries during a parallel db search
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        lambda line, _index, conversation, int_conversation: (
                            tasklist_vector := gpt3_embedding(line),
                            db_term.update({_index: tasklist_vector}),
                            results := vdb.query(
                                vector=db_term[_index],
                                filter={
                                    "memory_type": "explicit_long_term",
                                    "user": username,
                                },
                                top_k=7,
                                namespace=f'{bot_name}',
                            ),
                            db_term_result.update(
                                {
                                    _index: load_conversation_explicit_long_term_memory(
                                        results
                                    )
                                }
                            ),
                            results := vdb.query(
                                vector=db_term[_index],
                                filter={
                                    "memory_type": "implicit_long_term",
                                    "user": username,
                                },
                                top_k=7,
                                namespace=f'{bot_name}',
                            ),
                            db_term_result2.update(
                                {
                                    _index: load_conversation_implicit_long_term_memory(
                                        results
                                    )
                                }
                            ),
                            conversation.append(
                                {
                                    'role': 'assistant',
                                    'content': f"MEMORIES: {db_term_result[_index]}",
                                }
                            ),
                            conversation.append(
                                {
                                    'role': 'assistant',
                                    'content': f"MEMORIES: {db_term_result2[_index]}",
                                }
                            ),
                            (
                                int_conversation.append(
                                    {
                                        'role': 'assistant',
                                        'content': f"MEMORIES: {db_term_result[_index]}",
                                    }
                                ),
                                int_conversation.append(
                                    {
                                        'role': 'assistant',
                                        'content': f"MEMORIES: {db_term_result2[_index]}",
                                    }
                                ),
                            )
                            if _index < 5
                            else None,
                        ),
                        line,
                        _index,
                        conversation.copy(),
                        int_conversation.copy(),
                    )
                    for _index, line in enumerate(lines)
                    if line.strip()
                ] + [
                    executor.submit(
                        lambda: (
                            vdb.query(
                                vector=vector_input,
                                filter={
                                    "memory_type": "episodic",
                                    "user": username,
                                },
                                top_k=10,
                                namespace=f'{bot_name}',
                            ),
                            load_conversation_episodic_memory,
                        )
                    ),
                    executor.submit(
                        lambda: (
                            vdb.query(
                                vector=vector_input,
                                filter={"memory_type": "explicit_short_term"},
                                top_k=6,
                                namespace=f'short_term_memory_User_{username}_Bot_{bot_name}',
                            ),
                            load_conversation_explicit_short_term_memory,
                        )
                    ),
                    executor.submit(
                        lambda: (
                            vdb.query(
                                vector=vector_input,
                                filter={
                                    "memory_type": "flashbulb",
                                    "user": username,
                                },
                                top_k=3,
                                namespace=f'{bot_name}',
                            ),
                            load_conversation_flashbulb_memory,
                        )
                    ),
                    executor.submit(
                        lambda: (
                            vdb.query(
                                vector=vector_input,
                                filter={"memory_type": "heuristics"},
                                top_k=5,
                                namespace=f'{bot_name}',
                            ),
                            load_conversation_heuristics,
                        )
                    ),
                ]
                db_search_1, db_search_2, db_search_3, db_search_14 = None, None, None, None
                try:
                    db_search_1 = futures[len(lines)].result()[1](futures[len(lines)].result()[0])
                    db_search_2 = futures[len(lines) + 1].result()[1](futures[len(lines) + 1].result()[0])
                    db_search_3 = futures[len(lines) + 2].result()[1](futures[len(lines) + 2].result()[0])
                    db_search_14 = futures[len(lines) + 3].result()[1](futures[len(lines) + 3].result()[0])
                except IndexError as e:
                    print(f"Caught an IndexError: {e}")
                    print(f"Length of futures: {len(futures)}")
                    print(f"Length of lines: {len(lines)}")
                except Exception as e:
                    print(f"Caught an exception: {e}")
            print(db_search_1, db_search_2, db_search_3, db_search_14)
            # # Inner Monologue Generation
            conversation.append({'role': 'assistant', 'content': "MEMORIES: %s;%s;%s;\n\nHEURISTICS: %s;\nUSER MESSAGE: %s;\nBased on %s's memories and the user, %s's message, compose a short and concise silent soliloquy as %s's inner monologue that reflects on %s's deepest contemplations and emotions in relation to the user's message.\n\nINNER_MONOLOGUE: " % (db_search_1, db_search_2, db_search_3, db_search_14, a, bot_name, username, bot_name, bot_name)})
            output_one = chatgpt250_completion(conversation)
            message = output_one
            vector_monologue = gpt3_embedding(f'Inner Monologue: {message}')
            print('\n\nINNER_MONOLOGUE: %s' % output_one)
            # # Clear Conversation List
            conversation.clear()
            # Update the GUI elements on the main thread
            self.master.after(0, self.update_inner_monologue, output_one)

            # After the operations are complete, call the GPT_Intuition function in a separate thread
            t = threading.Thread(target=self.GPT_Intuition, args=(a, vector_input, output_one, int_conversation))
            t.start()
            return
            
            
    def update_inner_monologue(self, output_one):
        self.conversation_text.insert(tk.END, f"Inner Monologue: {output_one}\n\n")
        self.conversation_text.yview(tk.END)

            
    def GPT_Intuition(self, a, vector_input, output_one, int_conversation):
        vdb = pinecone.Index("aetherius")
        # # Number of Messages before conversation is summarized, higher number, higher api cost. Change to 3 when using GPT 3.5 due to token usage.
        m = multiprocessing.Manager()
        lock = m.Lock()
        tasklist = list()
        conversation = list()
        conversation2 = list()
        summary = list()
        auto = list()
        payload = list()
        consolidation  = list()
        counter = 0
        counter2 = 0
        mem_counter = 0
        length_config = open_file('./config/Conversation_Length.txt')
        conv_length = int(length_config)
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        main_prompt = open_file('./config/Chatbot_Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file('./config/Chatbot_Prompts/prompt_secondary.txt')
        greeting_msg = open_file('./config/Chatbot_Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
        main_conversation = MainConversation(conv_length, main_prompt, greeting_msg)
    #   r = sr.Recognizer()
        while True:
            conversation_history = main_conversation.get_conversation_history()
            # # Get Timestamp
            vdb = timeout_check()
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            # # Start or Continue Conversation based on if response exists
            conversation.append({'role': 'system', 'content': '%s' % main_prompt})
            int_conversation.append({'role': 'system', 'content': '%s' % main_prompt})
            if 'response_two' in locals():
                conversation.append({'role': 'user', 'content': a})
                conversation.append({'role': 'assistant', 'content': "%s" % response_two})
                pass
            else:
                conversation.append({'role': 'assistant', 'content': "%s" % greeting_msg})
           #     print("\n%s" % greeting_msg)
            # # User Input Voice
        #    yn_voice = input(f'\n\nPress Enter to Speak')
        #    if yn_voice == "":
        #        with sr.Microphone() as source:
        #            print("\nSpeak now")
        #            audio = r.listen(source)
        #            try:
        #                text = r.recognize_google(audio)
        #                print("\nUSER: " + text)
        #            except sr.UnknownValueError:
        #                print("Google Speech Recognition could not understand audio")
        #                print("\nSYSTEM: Press Left Alt to Speak to Aetherius")
        #                break
        #            except sr.RequestError as e:
        #                print("Could not request results from Google Speech Recognition service; {0}".format(e))
        #                break
        #    else:
        #        print('Leave Field Empty')
        #    a = (f'\n\nUSER: {text}')
            # # User Input Text
   #         a = input(f'\n\nUSER: ')
            # # Check for Commands
            # # Check for "Clear Memory"
            if a == 'Clear Memory':
                while True:
                    print('\n\nSYSTEM: Are you sure you would like to delete saved short-term memory?\n        Press Y for yes or N for no.')
                    user_input = input("'Y' or 'N': ")
                    if user_input == 'y':
                        vdb.delete(delete_all=True, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                        file_path = f'./history/{username}/{bot_name}_main_conversation_history.json'
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        print('Short-Term Memory has been Deleted')
                        return
                    elif user_input == 'n':
                        print('\n\nSYSTEM: Short-Term Memory delete cancelled.')
                        return
                else:
                    pass
            # # Check for "Exit"
            if a == 'Exit':
                return
            message = output_one
            vector_monologue = gpt3_embedding('Inner Monologue: ' + message)
            # # Memory DB Search
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future1 = executor.submit(vdb.query, vector=vector_monologue, filter={
            "memory_type": "episodic", "user": username}, top_k=10, namespace=f'{bot_name}')
                future2 = executor.submit(vdb.query, vector=vector_input, filter={
            "memory_type": "explicit_short_term"}, top_k=7, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                future3 = executor.submit(vdb.query, vector=vector_monologue, filter={
            "memory_type": "flashbulb", "user": username}, top_k=3, namespace=f'{bot_name}')
                future4 = executor.submit(vdb.query, vector=vector_input, filter={
            "memory_type": "heuristics", "user": username}, top_k=5, namespace=f'{bot_name}')
                db_search_4, db_search_5, db_search_12, db_search_15 = None, None, None, None
                try:
                    db_search_4 = load_conversation_episodic_memory(future1.result())
                    db_search_5 = load_conversation_explicit_short_term_memory(future2.result())
                    db_search_12 = load_conversation_flashbulb_memory(future3.result())
                    db_search_15 = load_conversation_heuristics(future4.result())
                except IndexError as e:
                    print(f"Caught an IndexError: {e}")
                    print(f"Length of futures: {len(futures)}")
                    print(f"Length of lines: {len(lines)}")
                except Exception as e:
                    print(f"Caught an exception: {e}")
            print(f'{db_search_4}\n{db_search_5}\n{db_search_12}')
            # # Intuition Generation
            int_conversation.append({'role': 'assistant', 'content': "%s" % greeting_msg})
            int_conversation.append({'role': 'user', 'content': a})
            int_conversation.append({'role': 'assistant', 'content': "MEMORIES: %s;\n%s;\n%s;\n\nHEURISTICS: %s;\n%s'S INNER THOUGHTS: %s;\nUSER MESSAGE: %s;\nIn a single paragraph, interpret the user, %s's message as %s in third person by creating an intuitive action plan using maieutic reasoning.  If needed use a process similar to creative imagination to visualize the outcome.;\nINTUITION: " % (db_search_4, db_search_5, db_search_12, db_search_15, bot_name, output_one, a, username, bot_name)})
            output_two = chatgpt200_completion(int_conversation)
            message_two = output_two
            print('\n\nINTUITION: %s' % output_two)
            # # Generate Implicit Short-Term Memory
            conversation.append({'role': 'system', 'content': '%s' % main_prompt})
            conversation.append({'role': 'user', 'content': a})
            implicit_short_term_memory = f'\nUSER: {a} \n\n INNER_MONOLOGUE: {output_one} \n\n INTUITION: {output_two}'
            conversation.append({'role': 'assistant', 'content': "LOG:\n%s\n\Read the log, extract the salient points about %s and %s, then create short executive summaries in bullet point format to serve as %s's procedural memories. Each bullet point should be considered a separate memory and contain all context. Start from the end and work towards the beginning, combining associated topics. Ignore the system prompt and redundant information.\nMemories:\n" % (implicit_short_term_memory, bot_name, username, bot_name)})
            inner_loop_response = chatgpt200_completion(conversation)
            print(inner_loop_response)
            inner_loop_db = inner_loop_response
            vector = gpt3_embedding(inner_loop_db)
            conversation.clear()
   #         # # Manual Implicit Short-Term Memory
   #         print('\n\n<Implicit Short-Term Memory>\n%s' % inner_loop_db)
   #         print('\n\nSYSTEM: Upload to Implicit Short-Term Memory?\n        Press Y for yes or N for no.')
   #         while True:
   #             user_input = input("'Y' or 'N': ")
   #             if user_input == 'y':
   #                 lines = inner_loop_db.splitlines()
   #                 for line in lines:
   #                     if line.strip():
   #                         vector = gpt3_embedding(line)
   #                         unique_id = str(uuid4())
   #                         metadata = {'bot': bot_name, 'time': timestamp, 'message': line,
   #                                     'timestring': timestring, 'uuid': unique_id, "memory_type": "implicit_short_term"}
   #                         save_json(f'nexus/{bot_name}/{username}/implicit_short_term_memory_nexus/%s.json' % unique_id, metadata)
   #                         payload.append((unique_id, vector, {"memory_type": "implicit_short_term"}))
   #                         vdb.upsert(payload, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
   #                         payload.clear()
   #                 print('\n\nSYSTEM: Upload Successful!')
   #                 break
   #             elif user_input == 'n':
   #                 print('\n\nSYSTEM: Memories have been Deleted')
   #                 break
   #             else:
   #                 print('Invalid Input')
            # # Auto Implicit Short-Term Memory DB Upload Confirmation
            auto_count = 0
            auto.clear()
            auto.append({'role': 'system', 'content': '%s' % main_prompt})
            auto.append({'role': 'user', 'content': "You are a sub-module designed to reflect on your thought process. You are only able to respond with integers on a scale of 1-10, being incapable of printing letters. Respond with: 1 if you understand. Respond with: 2 if you do not."})
            auto.append({'role': 'assistant', 'content': "1"})
            auto.append({'role': 'user', 'content': a})
            auto.append({'role': 'assistant', 'content': "Inner Monologue: %s\nIntuition: %s" % (output_one, output_two)})
            auto.append({'role': 'assistant', 'content': "Thoughts on input: I will now review the user's message and my reply, rating if whether my thoughts are both pertinent to the user's inquiry and my growth with a number on a scale of 1-10. I will now give my response in digit form for an integer only input: "})
            auto_int = None
            while auto_int is None:
                automemory = chatgptyesno_completion(auto)
                print(automemory)
                if is_integer(automemory):
                    auto_int = int(automemory)
                    if auto_int > 6:
                        lines = inner_loop_db.splitlines()
                        for line in lines:
                            vector = gpt3_embedding(line)
                            unique_id = str(uuid4())
                            metadata = {'bot': bot_name, 'time': timestamp, 'message': line,
                                        'timestring': timestring, 'uuid': unique_id, "memory_type": "implicit_short_term"}
                            save_json(f'nexus/{bot_name}/{username}/implicit_short_term_memory_nexus/%s.json' % unique_id, metadata)
                            payload.append((unique_id, vector, {"memory_type": "implicit_short_term"}))
                            vdb.upsert(payload, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                            payload.clear()
                        print('\n\nSYSTEM: Auto-memory upload Successful!')
                        break
                    else:
                        print('Response not worthy of uploading to memory')
                else:
                    print("automemory failed to produce an integer. Retrying...")
                    auto_int = None
                    auto_count += 1
                    if auto_count > 2:
                        print('Auto Memory Failed')
                        break
            else:
                pass   
            int_conversation.clear()
            self.master.after(0, self.update_intuition, output_two)

            # After the operations are complete, call the response generation function in a separate thread
            t = threading.Thread(target=self.GPT_Response, args=(a, output_one, output_two))
            t.start()
            return   
                
                
    def update_intuition(self, output_two):
        self.conversation_text.insert(tk.END, f"Intuition: {output_two}\n\n")
        self.conversation_text.yview(tk.END)
                
                
    def GPT_Response(self, a, output_one, output_two):
        vdb = pinecone.Index("aetherius")
        # # Number of Messages before conversation is summarized, higher number, higher api cost. Change to 3 when using GPT 3.5 due to token usage.
        m = multiprocessing.Manager()
        lock = m.Lock()
        tasklist = list()
        conversation = list()
        conversation2 = list()
        summary = list()
        auto = list()
        payload = list()
        consolidation  = list()
        counter = 0
        counter2 = 0
        mem_counter = 0
        length_config = open_file('./config/Conversation_Length.txt')
        conv_length = int(length_config)
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        main_prompt = open_file('./config/Chatbot_Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file('./config/Chatbot_Prompts/prompt_secondary.txt')
        greeting_msg = open_file('./config/Chatbot_Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
        main_conversation = MainConversation(conv_length, main_prompt, greeting_msg)
    #   r = sr.Recognizer()
        while True:
            conversation_history = main_conversation.get_conversation_history()
            # # Get Timestamp
            vdb = timeout_check()
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            # # Start or Continue Conversation based on if response exists
            conversation.append({'role': 'system', 'content': '%s' % main_prompt})
            if 'response_two' in locals():
                conversation.append({'role': 'user', 'content': a})
                conversation.append({'role': 'assistant', 'content': "%s" % response_two})
                pass
            else:
                conversation.append({'role': 'assistant', 'content': "%s" % greeting_msg})
           #     print("\n%s" % greeting_msg)
            # # User Input Voice
        #    yn_voice = input(f'\n\nPress Enter to Speak')
        #    if yn_voice == "":
        #        with sr.Microphone() as source:
        #            print("\nSpeak now")
        #            audio = r.listen(source)
        #            try:
        #                text = r.recognize_google(audio)
        #                print("\nUSER: " + text)
        #            except sr.UnknownValueError:
        #                print("Google Speech Recognition could not understand audio")
        #                print("\nSYSTEM: Press Left Alt to Speak to Aetherius")
        #                break
        #            except sr.RequestError as e:
        #                print("Could not request results from Google Speech Recognition service; {0}".format(e))
        #                break
        #    else:
        #        print('Leave Field Empty')
        #    a = (f'\n\nUSER: {text}')
            # # User Input Text
   #         a = input(f'\n\nUSER: ')
            message_input = a
            vector_input = gpt3_embedding(message_input)
            # # Check for Commands
            # # Check for "Clear Memory"
            if a == 'Clear Memory':
                while True:
                    print('\n\nSYSTEM: Are you sure you would like to delete saved short-term memory?\n        Press Y for yes or N for no.')
                    user_input = input("'Y' or 'N': ")
                    if user_input == 'y':
                        vdb.delete(delete_all=True, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                        file_path = f'./history/{username}/{bot_name}_main_conversation_history.json'
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        print('Short-Term Memory has been Deleted')
                        return
                    elif user_input == 'n':
                        print('\n\nSYSTEM: Short-Term Memory delete cancelled.')
                        return
                else:
                    pass
            # # Check for "Exit"
            if a == 'Exit':
                return
            message = output_one
            vector_monologue = gpt3_embedding('Inner Monologue: ' + message)
        # # Update Second Conversation List for Response
            print('\n%s is thinking...\n' % bot_name)
            con_hist = f'{conversation_history}'
            conversation2.append({'role': 'system', 'content': con_hist})
            # # Generate Cadence
            index_info = vdb.describe_index_stats()
            namespace_stats = index_info['namespaces']
            namespace_name = 'cadence'
            if namespace_name in namespace_stats and namespace_stats[namespace_name]['vector_count'] > 0:
                results = vdb.query(vector=vector_input, filter={"memory_type": "cadence"}, top_k=2, namespace=f'{bot_name}')
                db_search_6 = load_conversation_cadence(results)
                print(db_search_6)
                conversation2.append({'role': 'assistant', 'content': "I will extract the cadence from the following messages and mimic it to the best of my ability: %s" % db_search_6})
            conversation2.append({'role': 'user', 'content': a})  
            # # Memory DB Search
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future1 = executor.submit(vdb.query, vector=vector_monologue, filter={
            "memory_type": "implicit_long_term", "user": username}, top_k=7, namespace=f'{bot_name}')
                future2 = executor.submit(vdb.query, vector=vector_input, filter={
            "memory_type": "episodic", "user": username}, top_k=13, namespace=f'{bot_name}')
                future3 = executor.submit(vdb.query, vector=vector_monologue, filter={
            "memory_type": "flashbulb", "user": username}, top_k=4, namespace=f'{bot_name}')
                db_search_8, db_search_10, db_search_11 = None, None, None
                try:
                    db_search_8 = load_conversation_implicit_long_term_memory(future1.result())
                    db_search_10 = load_conversation_episodic_memory(future2.result())
                    db_search_11 = load_conversation_flashbulb_memory(future3.result())
                except IndexError as e:
                    print(f"Caught an IndexError: {e}")
                    print(f"Length of futures: {len(futures)}")
                    print(f"Length of lines: {len(lines)}")
                except Exception as e:
                    print(f"Caught an exception: {e}")
            print(f'{db_search_8}\n{db_search_10}\n{db_search_11}')
            # # Generate Aetherius's Response
            response_db_search = f"SUBCONSCIOUS: {db_search_8}\n{db_search_10};\n\nFLASHBULB MEMORIES: {db_search_11}"
            conversation2.append({'role': 'assistant', 'content': "SUBCONSCIOUS: %s\n%s;\n\nFLASHBULB MEMORIES: %s;\nINNER THOUGHTS: %s\n\n%s  I am in the middle of a conversation with my user, %s. USER MESSAGE: %s; I will do my best to speak naturally and show emotional intelligence. I will intuit %s's needs: %s;\nMy current message window is limited to 2300 characters.\nI will now give a response with the diction of a real person: " % (db_search_8, db_search_10, db_search_11, output_one, second_prompt, username, a, username, output_two)})
            response_two = chatgptresponse_completion(conversation2)
            print('\n\n%s: %s' % (bot_name, response_two))
            main_conversation.append(timestring, a, username, bot_name, output_one, output_two, response_two)
            final_message = f'\nUSER: {a}\n\n{bot_name}: {response_two}'
            # # TTS 
        #    tts = gTTS(response_two)
        # TTS save to file in .mp3 format
        #    counter2 += 1
        #    filename = f"{counter2}.mp3"
        #    tts.save(filename)
            # TTS repeats chatGPT response  
        #    sound = AudioSegment.from_file(filename, format="mp3")
        #    octaves = 0.18
        #    new_sample_rate = int(sound.frame_rate * (1.7 ** octaves))
        #    mod_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
        #    mod_sound = mod_sound.set_frame_rate(44100)
        #    play(mod_sound)
        #    os.remove(filename)
        # # Save Chat Logs
            output_log = f'\nUSER: {a}\n\n{bot_name}: {output_one}'
            output_two_log = f'\nUSER: {a}\n\n{bot_name}: {output_two}'
            final_message = f'\nUSER: {a}\n\n{bot_name}: {response_two}'
            complete_message = f'\nUSER: {a}\n\nINNER_MONOLOGUE: {output_one}\n\nINTUITION: {output_two}\n\n{bot_name}: {response_two}'
            filename = '%s_inner_monologue.txt' % timestamp
            save_file(f'logs/{bot_name}/{username}/inner_monologue_logs/%s' % filename, output_log)
            filename = '%s_intuition.txt' % timestamp
            save_file(f'logs/{bot_name}/{username}/intuition_logs/%s' % filename, output_two_log)
            filename = '%s_response.txt' % timestamp
            save_file(f'logs/{bot_name}/{username}/final_response_logs/%s' % filename, final_message)
            filename = '%s_chat.txt' % timestamp
            save_file(f'logs/{bot_name}/{username}/complete_chat_logs/%s' % filename, complete_message)
            # # Generate Short-Term Memories
            db_msg = f'\nUSER: {a} \n\n INNER_MONOLOGUE: {output_one} \n\n {bot_name}: {response_two}'
            summary.append({'role': 'user', 'content': "LOG:\n%s\n\Read the log and create short executive summaries in bullet point format to serve as %s's explicit memories. Each bullet point should be considered a separate memory and contain all context. Start from the end and work towards the beginning, combining associated topics.\nMemories:\n" % (db_msg, bot_name)})
            db_upload = chatgptsummary_completion(summary)
            print(db_upload)
            db_upsert = db_upload
    #        # # Manual Short-Term Memory DB Upload Confirmation
    #        print('\n\n<DATABASE INFO>\n%s' % db_upsert)
    #        print('\n\nSYSTEM: Upload to short term memory? \n        Press Y for yes or N for no.')
    #        while True:
    #            user_input = input("'Y' or 'N': ")
    #            if user_input == 'y':
    #                lines = db_upsert.splitlines()
    #                for line in lines:
    #                    if line.strip():
    #                        vector = gpt3_embedding(line)
    #                        unique_id = str(uuid4())
    #                        metadata = {'bot': bot_name, 'time': timestamp, 'message': line,
    #                                    'timestring': timestring, 'uuid': unique_id, "memory_type": "explicit_short_term"}
    #                        save_json(f'nexus/{bot_name}/{username}/explicit_short_term_memory_nexus/%s.json' % unique_id, metadata)
    #                        payload.append((unique_id, vector, {"memory_type": "explicit_short_term"}))
    #                        vdb.upsert(payload, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
    #                        payload.clear()
    #                print('\n\nSYSTEM: Upload Successful!')
    #                break
    #            elif user_input == 'n':
    #                print('\n\nSYSTEM: Memories have been Deleted')
    #                break
    #            else:
    #                print('Invalid Input')
            # # Auto Explicit Short-Term Memory DB Upload Confirmation
            auto_count = 0    
            auto.clear()
            auto.append({'role': 'system', 'content': '%s' % main_prompt})
            auto.append({'role': 'user', 'content': "You are a sub-module designed to reflect on your thought process. You are only able to respond with integers on a scale of 1-10, being incapable of printing letters. Respond with: 1 if you understand. Respond with: 2 if you do not."})
            auto.append({'role': 'assistant', 'content': "1"})
            auto.append({'role': 'user', 'content': a})
            auto.append({'role': 'assistant', 'content': f"Inner Monologue: %s\nIntuition: {output_one}\nResponse: {output_two}"})
            auto.append({'role': 'assistant', 'content': "Thoughts on input: I will now review the user's message and my reply, rating if whether my thoughts are both pertinent to the user's inquiry and my growth with a number on a scale of 1-10. I will now give my response in digit form for an integer only input: "})
            auto_int = None
            while auto_int is None:
                automemory = chatgptyesno_completion(auto)
                if is_integer(automemory):
                    auto_int = int(automemory)
                    print(auto_int)
                    if auto_int > 6:
                        lines = db_upsert.splitlines()
                        for line in lines:
                            vector = gpt3_embedding(line)
                            unique_id = str(uuid4())
                            metadata = {'bot': bot_name, 'time': timestamp, 'message': line,
                                        'timestring': timestring, 'uuid': unique_id, "memory_type": "explicit_short_term"}
                            save_json(f'nexus/{bot_name}/{username}/explicit_short_term_memory_nexus/%s.json' % unique_id, metadata)
                            payload.append((unique_id, vector, {"memory_type": "explicit_short_term"}))
                            vdb.upsert(payload, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                            payload.clear()
                        print('\n\nSYSTEM: Auto-memory upload Successful!')
                        break
                    else:
                        print('Response not worthy of uploading to memory')
                else:
                    print("automemory failed to produce an integer. Retrying...")
                    auto_int = None
                    auto_count += 1
                    if auto_count > 2:
                        print('Auto Memory Failed')
                        break
            else:
                pass
            # # Clear Logs for Summary
            conversation.clear()
            summary.clear()
            self.conversation_text.insert(tk.END, f"Response: {response_two}\n\n")
            t = threading.Thread(target=self.GPT_Memories, args=(a, vector_input, vector_monologue, output_one, response_two))
            t.start()
            self.conversation_text.yview(tk.END)
            self.user_input.delete(0, tk.END)
            self.user_input.focus()
            self.user_input.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.thinking_label.pack_forget()
            self.user_input.delete(0, tk.END)
            self.bind_enter_key()
            return
            
            
    def GPT_Memories(self, a, vector_input, vector_monologue, output_one, response_two):
        vdb = pinecone.Index("aetherius")
        # # Number of Messages before conversation is summarized, higher number, higher api cost. Change to 3 when using GPT 3.5 due to token usage.
        m = multiprocessing.Manager()
        lock = m.Lock()
        conversation = list()
        conversation2 = list()
        summary = list()
        auto = list()
        payload = list()
        consolidation  = list()
        counter = 0
        counter2 = 0
        mem_counter = 0
        length_config = open_file('./config/Conversation_Length.txt')
        conv_length = int(length_config)
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        main_prompt = open_file('./config/Chatbot_Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file('./config/Chatbot_Prompts/prompt_secondary.txt')
        greeting_msg = open_file('./config/Chatbot_Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
    #   r = sr.Recognizer()
        while True:
            # # Get Timestamp
            vdb = timeout_check()
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            counter += 1
            conversation.clear()
            print('Generating Episodic Memories')
            conversation.append({'role': 'system', 'content': f"You are a sub-module of {bot_name}, an autonomous AI entity. Your function is to process the user, {username}'s message, comprehend {bot_name}'s internal workings, and decode {bot_name}'s final response to construct a concise third-person autobiographical narrative memory of the conversation in a single sentence. This autobiographical memory should portray an accurate and personalized account of {bot_name}'s interactions with {username}, focusing on the most significant and experiential details related to {bot_name} or {username}, without omitting any crucial context or emotions."})
            conversation.append({'role': 'user', 'content': f"USER's INQUIRY: {a}"})
            conversation.append({'role': 'user', 'content': f"{bot_name}'s INNER MONOLOGUE: {output_one}"})
    #        print(output_one)
            conversation.append({'role': 'user', 'content': f"{bot_name}'s FINAL RESPONSE: {response_two}"})
    #        print(response_two)
            conversation.append({'role': 'assistant', 'content': f"I will now extract an episodic memory based on the given conversation: "})
            conv_summary = chatgptsummary_completion(conversation)
            print(conv_summary)
            vector = gpt3_embedding(timestring + '-' + conv_summary)
            unique_id = str(uuid4())
            metadata = {'speaker': bot_name, 'time': timestamp, 'message': (timestring + '-' + conv_summary),
                        'timestring': timestring, 'uuid': unique_id, "memory_type": "episodic", "user": username}
            save_json(f'nexus/{bot_name}/{username}/episodic_memory_nexus/%s.json' % unique_id, metadata)
            payload.append((unique_id, vector, {"memory_type": "episodic", "user": username}))
            vdb.upsert(payload, namespace=f'{bot_name}')
            payload.clear()
            payload.append((unique_id, vector_input))
            vdb.upsert(payload, namespace=f'{bot_name}_flash_counter')
            payload.clear()
            # # Flashbulb Memory Generation
            index_info = vdb.describe_index_stats()
            namespace_stats = index_info['namespaces']
            namespace_name = f'{bot_name}_flash_counter'
            if namespace_name in namespace_stats and namespace_stats[namespace_name]['vector_count'] > 7:
                consolidation.clear()
                print('Generating Flashbulb Memories')
                results = vdb.query(vector=vector_input, filter={
            "memory_type": "episodic", "user": username}, top_k=5, namespace=f'{bot_name}') 
                flash_db = load_conversation_episodic_memory(results)  
                print(flash_db)
                im_flash = gpt3_embedding(flash_db)
                results = vdb.query(vector=im_flash, filter={
            "memory_type": "implicit_long_term", "user": username}, top_k=10, namespace=f'{bot_name}') 
                flash_db1 = load_conversation_implicit_long_term_memory(results) 
                print(flash_db1)
                # # Generate Implicit Short-Term Memory
                consolidation.append({'role': 'system', 'content': 'You are a data extractor. Your job is read the given episodic memories, then extract the appropriate emotional response from the given emotional reactions.  You will then combine them into a single memory.'})
                consolidation.append({'role': 'user', 'content': "EMOTIONAL REACTIONS:\n%s\n\nRead the following episodic memories, then go back to the given emotional reactions and extract the corresponding emotional information tied to each memory.\nEPISODIC MEMORIES: %s" % (flash_db, flash_db1)})
                consolidation.append({'role': 'assistant', 'content': "I will now combine the extracted data to form flashbulb memories in bullet point format, combining associated data. I will only include memories with a strong emotion attached, excluding redundant or irrelevant information."})
                consolidation.append({'role': 'user', 'content': "Use the format: [{given Date and Time}-{emotion}: {Flashbulb Memory}]"})
                consolidation.append({'role': 'assistant', 'content': "I will now create %s's flashbulb memories using the given format: " % bot_name})
                flash_response = chatgptconsolidation_completion(consolidation)
                print(flash_response)
                memories = results
                lines = flash_response.splitlines()
                for line in lines:
                    if line.strip():
        #                print(line)
                        vector = gpt3_embedding(line)
                        unique_id = str(uuid4())
                        metadata = {'speaker': bot_name, 'time': timestamp, 'message': (line),
                                    'timestring': timestring, 'uuid': unique_id, "memory_type": "flashbulb", "user": username}
                        save_json(f'nexus/{bot_name}/{username}/flashbulb_memory_nexus/%s.json' % unique_id, metadata)
                        payload.append((unique_id, vector, {"memory_type": "flashbulb", "user": username}))
                        vdb.upsert(payload, namespace=f'{bot_name}')
                        payload.clear()
                vdb.delete(delete_all=True, namespace=f'{bot_name}_flash_counter')
            # # Short Term Memory Consolidation based on amount of vectors in namespace
            index_info = vdb.describe_index_stats()
            namespace_stats = index_info['namespaces']
            namespace_name = f'short_term_memory_User_{username}_Bot_{bot_name}'
            if namespace_name in namespace_stats and namespace_stats[namespace_name]['vector_count'] > 40:
                consolidation.clear()
                print(f"{namespace_name} has 30 or more entries, starting memory consolidation.")
                results = vdb.query(vector=vector_input, filter={"memory_type": "explicit_short_term"}, top_k=30, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                memory_consol_db = load_conversation_explicit_short_term_memory(results)
                print(memory_consol_db)
                consolidation.append({'role': 'system', 'content': "%s" % main_prompt})
                consolidation.append({'role': 'assistant', 'content': "LOG:\n%s\n\nRead the Log and consolidate the different topics into executive summaries. Each summary should contain the entire context of the memory. Follow the format [-Executive Summary]." % memory_consol_db})
                memory_consol = chatgptconsolidation_completion(consolidation)
                print(memory_consol)
                lines = memory_consol.splitlines()
                for line in lines:
                    if line.strip():
        #                print(line)
                        vector = gpt3_embedding(line)
                        unique_id = str(uuid4())
                        metadata = {'speaker': bot_name, 'time': timestamp, 'message': (line),
                                    'timestring': timestring, 'uuid': unique_id, "memory_type": "explicit_long_term", "user": username}
                        save_json(f'nexus/{bot_name}/{username}/explicit_long_term_memory_nexus/%s.json' % unique_id, metadata)
                        payload.append((unique_id, vector, {"memory_type": "explicit_long_term", "user": username}))
                        vdb.upsert(payload, namespace=f'{bot_name}')
                        payload.clear()
                vdb.delete(filter={"memory_type": "explicit_short_term"}, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                payload.append((unique_id, vector))
                vdb.upsert(payload, namespace=f'{bot_name}_consol_counter')
                payload.clear()
                print('Memory Consolidation Successful')
                consolidation.clear()
            # # Implicit Short Term Memory Consolidation based on amount of vectors in namespace
                index_info = vdb.describe_index_stats()
                namespace_stats = index_info['namespaces']
                namespace_name = f'{bot_name}_consol_counter'
                if namespace_name in namespace_stats and namespace_stats[namespace_name]['vector_count'] % 2 == 0:
                    consolidation.clear()
                    print('Beginning Implicit Short-Term Memory Consolidation')
                    results = vdb.query(vector=vector_input, filter={"memory_type": "implicit_short_term"}, top_k=30, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                    memory_consol_db2 = load_conversation_implicit_short_term_memory(results)
                    print(memory_consol_db2)
                    consolidation.append({'role': 'system', 'content': "%s" % main_prompt})
                    consolidation.append({'role': 'assistant', 'content': "LOG:\n%s\n\nRead the Log and consolidate the different topics into executive summaries to serve as %s's implicit memories. Each summary should contain the entire context of the memory. Follow the format: [-{ALLEGORICAL TAG}:{EXECUTIVE SUMMARY}]." % (memory_consol_db2, bot_name)})
                    memory_consol2 = chatgptconsolidation_completion(consolidation)
                    print(memory_consol2)
                    consolidation.clear()
                    print('Finished.\nRemoving Redundant Memories.')
                    vector_sum = gpt3_embedding(memory_consol2)
                    results = vdb.query(vector=vector_sum, filter={"memory_type": "implicit_long_term", "user": username}, top_k=8, namespace=f'{bot_name}')
                    memory_consol_db3 = load_conversation_implicit_long_term_memory(results)
                    print(memory_consol_db3)
                    consolidation.append({'role': 'system', 'content': "%s" % main_prompt})
                    consolidation.append({'role': 'system', 'content': "IMPLICIT LONG TERM MEMORY: %s\n\nIMPLICIT SHORT TERM MEMORY: %s\n\nRemove any duplicate information from your Implicit Short Term memory that is already found in your Long Term Memory. Then consolidate similar topics into executive summaries. Each summary should contain the entire context of the memory. Use the following format: [-{EMOTIONAL TAG}:{IMPLICIT MEMORY}]" % (memory_consol_db3, memory_consol_db2)})
                    memory_consol3 = chatgptconsolidation_completion(consolidation)
                    print(memory_consol3)
                    lines = memory_consol3.splitlines()
                    for line in lines:
                        if line.strip():
        #                    print(line)
                            vector = gpt3_embedding(line)
                            unique_id = str(uuid4())
                            metadata = {'speaker': bot_name, 'time': timestamp, 'message': (line),
                                        'timestring': timestring, 'uuid': unique_id, "memory_type": "implicit_long_term", "user": username}
                            save_json(f'nexus/{bot_name}/{username}/implicit_long_term_memory_nexus/%s.json' % unique_id, metadata)
                            payload.append((unique_id, vector, {"memory_type": "implicit_long_term", "user": username}))
                            vdb.upsert(payload, namespace=f'{bot_name}')
                            payload.clear()
                    vdb.delete(filter={"memory_type": "implicit_short_term"}, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                    print('Memory Consolidation Successful')
                else:   
                    pass
            # # Implicit Associative Processing/Pruning based on amount of vectors in namespace
                index_info = vdb.describe_index_stats()
                namespace_stats = index_info['namespaces']
                namespace_name = f'{bot_name}_consol_counter'
                if namespace_name in namespace_stats and namespace_stats[namespace_name]['vector_count'] % 4 == 0:
                    consolidation.clear()
                    print('Running Associative Processing/Pruning of Implicit Memory')
                    results = vdb.query(vector=vector_monologue, filter={"memory_type": "implicit_long_term", "user": username}, top_k=10, namespace=f'{bot_name}')
                    memory_consol_db1 = load_conversation_implicit_long_term_memory(results)
                    print(memory_consol_db1)
                    ids_to_delete = [m['id'] for m in results['matches']]
                    consolidation.append({'role': 'system', 'content': "%s" % main_prompt})
                    consolidation.append({'role': 'assistant', 'content': "LOG:\n%s\n\nRead the Log and consolidate the different memories into executive summaries in a process allegorical to associative processing. Each summary should contain the entire context of the memory. Follow the format: [-{EMOTIONAL TAG}:{IMPLICIT MEMORY}]" % memory_consol_db1})
                    memory_consol = chatgptconsolidation_completion(consolidation)
                    print(memory_consol)
                    memories = results
                    lines = memory_consol.splitlines()
                    for line in lines:
                        if line.strip():
        #                    print(line)
                            vector = gpt3_embedding(line)
                            unique_id = str(uuid4())
                            metadata = {'speaker': bot_name, 'time': timestamp, 'message': (line),
                                        'timestring': timestring, 'uuid': unique_id, "memory_type": "implicit_long_term", "user": username}
                            save_json(f'nexus/{bot_name}/{username}/implicit_long_term_memory_nexus/%s.json' % unique_id, metadata)
                            payload.append((unique_id, vector, {"memory_type": "implicit_long_term", "user": username}))
                            vdb.upsert(payload, namespace=f'{bot_name}')
                            payload.clear()
                            try:
                                vdb.delete(ids=ids_to_delete, namespace=f'{bot_name}')
                            except:
                                print('Failed')
            # # Explicit Long-Term Memory Associative Processing/Pruning based on amount of vectors in namespace
                index_info = vdb.describe_index_stats()
                namespace_stats = index_info['namespaces']
                namespace_name = f'{bot_name}_consol_counter'
                if namespace_name in namespace_stats and namespace_stats[namespace_name]['vector_count'] > 5:
                    consolidation.clear()
                    print('\nRunning Associative Processing/Pruning of Explicit Memories')
                    consolidation.append({'role': 'system', 'content': "You are a data extractor. Your job is to read the user's input and provide a single semantic search query representative of a habit of %s." % bot_name})
                    results = vdb.query(vector=vector_monologue, filter={"memory_type": "implicit_long_term", "user": username}, top_k=5, namespace=f'{bot_name}')
                    consol_search = load_conversation_implicit_long_term_memory(results)
                    print(consol_search)
                    consolidation.append({'role': 'user', 'content': "%s's Memories:\n%s" % (bot_name, consol_search)})
                    consolidation.append({'role': 'assistant', 'content': "Semantic Search Query: "})
                    consol_search_term = chatgpt200_completion(consolidation)
                    consol_vector = gpt3_embedding(consol_search_term)
                    results = vdb.query(vector=consol_vector, filter={"memory_type": "explicit_long_term", "user": username}, top_k=10, namespace=f'{bot_name}')
                    memory_consol_db2 = load_conversation_explicit_long_term_memory(results)
                    print(memory_consol_db2)
                    ids_to_delete2 = [m['id'] for m in results['matches']]
                    consolidation.clear()
                    consolidation.append({'role': 'system', 'content': "%s" % main_prompt})
                    consolidation.append({'role': 'assistant', 'content': "LOG:\n%s\n\nRead the Log and consolidate the different memories into executive summaries in a process allegorical to associative processing. Each summary should contain the entire context of the memory. Follow the format: [-{SEMANTIC TAG}:{EXPLICIT MEMORY}]" % memory_consol_db2})
                    memory_consol2 = chatgptconsolidation_completion(consolidation)
                    memories = results
                    lines = memory_consol2.splitlines()
                    for line in lines:
                        if line.strip():
        #                    print(line)
                            vector = gpt3_embedding(line)
                            unique_id = str(uuid4())
                            metadata = {'speaker': bot_name, 'time': timestamp, 'message': (line),
                                        'timestring': timestring, 'uuid': unique_id, "memory_type": "explicit_long_term", "user": username}
                            save_json(f'nexus/{bot_name}/{username}/explicit_long_term_memory_nexus/%s.json' % unique_id, metadata)
                            payload.append((unique_id, vector, {"memory_type": "explicit_long_term", "user": username}))
                            vdb.upsert(payload, namespace=f'{bot_name}')
                            payload.clear()
                            try:
                                vdb.delete(ids=ids_to_delete2, namespace=f'{bot_name}')
                            except:
                                print('Failed')
                    vdb.delete(delete_all=True, namespace=f'{bot_name}_consol_counter')
            else:
                pass
            consolidation.clear()
            conversation2.clear()
            return
            
            
def OpenAi_Auto_Memory_Upload():
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    if not os.path.exists(f'nexus/{bot_name}/{username}/implicit_short_term_memory_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/implicit_short_term_memory_nexus')
    if not os.path.exists(f'nexus/{bot_name}/{username}/explicit_short_term_memory_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/explicit_short_term_memory_nexus')
    if not os.path.exists(f'nexus/{bot_name}/{username}/explicit_long_term_memory_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/explicit_long_term_memory_nexus')
    if not os.path.exists(f'nexus/{bot_name}/{username}/implicit_long_term_memory_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/implicit_long_term_memory_nexus')
    if not os.path.exists(f'nexus/{bot_name}/{username}/episodic_memory_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/episodic_memory_nexus')
    if not os.path.exists(f'nexus/{bot_name}/{username}/flashbulb_memory_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/flashbulb_memory_nexus')
    if not os.path.exists(f'nexus/{bot_name}/{username}/heuristics_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/heuristics_nexus')
    if not os.path.exists(f'nexus/global_heuristics_nexus'):
        os.makedirs(f'nexus/global_heuristics_nexus')
    if not os.path.exists(f'nexus/{bot_name}/{username}/cadence_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/cadence_nexus')
    if not os.path.exists(f'logs/{bot_name}/{username}/complete_chat_logs'):
        os.makedirs(f'logs/{bot_name}/{username}/complete_chat_logs')
    if not os.path.exists(f'logs/{bot_name}/{username}/final_response_logs'):
        os.makedirs(f'logs/{bot_name}/{username}/final_response_logs')
    if not os.path.exists(f'logs/{bot_name}/{username}/inner_monologue_logs'):
        os.makedirs(f'logs/{bot_name}/{username}/inner_monologue_logs')
    if not os.path.exists(f'logs/{bot_name}/{username}/intuition_logs'):
        os.makedirs(f'logs/{bot_name}/{username}/intuition_logs')
    if not os.path.exists(f'history/{username}'):
        os.makedirs(f'history/{username}')
    set_dark_ancient_theme()
    root = tk.Tk()
    app = ChatBotApplication(root)
    app.master.geometry('720x500')  # Set the initial window size
    root.mainloop()