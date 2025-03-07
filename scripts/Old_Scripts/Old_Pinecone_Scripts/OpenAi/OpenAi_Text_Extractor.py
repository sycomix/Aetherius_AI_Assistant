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
from basic_functions import *
from tool_functions import *
import requests
import multiprocessing
import concurrent.futures
import threading
import shutil
from concurrent.futures import ThreadPoolExecutor
from PyPDF2 import PdfReader
from ebooklib import epub
import pytesseract
from PIL import Image
import customtkinter
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, font, filedialog
from bs4 import BeautifulSoup
import subprocess
import importlib.util
# import speech_recognition as sr
# from gtts import gTTS
# from playsound import playsound
# import pyttsx3
# from pydub import AudioSegment
# from pydub.playback import play
# from pydub import effects

def gpt3_embedding(content, engine='text-embedding-ada-002'):
    max_retry = 7
    retry = 0
    while True:
        try:
            content = content.encode(encoding='ASCII', errors='ignore').decode()  # fix any UNICODE errors
            response = openai.Embedding.create(input=content, engine=engine)
            vector = response['data'][0]['embedding']  # this is a normal list
            return vector
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                print(f"Exiting due to an error in ChatGPT: {oops}")
                exit(1)
            print(f'Error communicating with OpenAI: "{oops}" - Retrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)


def load_conversation_explicit_short_term_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = list()
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/explicit_short_term_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()
    
    
def load_conversation_explicit_long_term_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = list()
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/explicit_long_term_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()
    
    
def load_conversation_episodic_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = list()
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/episodic_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()  
    
    
def load_conversation_flashbulb_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = list()
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/flashbulb_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip() 
    
    
def load_conversation_heuristics(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = list()
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/heuristics_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()    


def load_conversation_implicit_short_term_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = list()
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/implicit_short_term_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()  
    
    
def load_conversation_cadence(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = list()
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/cadence_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip() 
    
    
def load_conversation_implicit_long_term_memory(results):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    result = list()
    for m in results['matches']:
        info = load_json(f'nexus/{bot_name}/{username}/implicit_long_term_memory_nexus/%s.json' % m['id'])
        result.append(info)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
    messages = [i['message'] for i in ordered]
    return '\n'.join(messages).strip()
    
def timeout_check():
    try:
        pinecone.init(api_key=open_file('api_keys/key_pinecone.txt'), environment=open_file('api_keys/key_pinecone_env.txt'))
        vdb = pinecone.Index("aetherius")
        return vdb
    except pinecone.exceptions.PineconeException as e:
        if "timed out" in str(e):
            print("Connection timed out. Reconnecting...")
            timeout_check()
        else:
            raise e

openai.api_key = open_file('api_keys/key_openai.txt')


pinecone.init(api_key=open_file('api_keys/key_pinecone.txt'), environment=open_file('api_keys/key_pinecone_env.txt'))
vdb = pinecone.Index("aetherius")


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
        entry = []
        entry.append(f"{timestring}-{username}: {a}")
        entry.append(f"{bot_name}'s Inner Monologue: {output_one}\n")
        entry.append(f"Intuition: {output_two}\n")
        entry.append(f"Response: {response_two}\n")
        self.running_conversation.append(entry)
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
        return self.main_conversation + [message for entry in self.running_conversation for message in entry]

  
  
  
  
  
class ChatBotApplication(tk.Frame):
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
        menu.add_command(label="Copy", command=self.copy_selected_text)
        # Add more menu items as needed
        
        # Display the menu at the clicked position
        menu.post(event.x_root, event.y_root)
        
        
    def display_conversation_history(self):
        pass
        
        
    def choose_bot_name(self):
        bot_name = simpledialog.askstring("Choose Bot Name", "Type a Bot Name:")
        if bot_name:
            file_path = "./config/prompt_bot_name.txt"
            with open(file_path, 'w') as file:
                file.write(bot_name)
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()  
        

    def choose_username(self):
        username = simpledialog.askstring("Choose Username", "Type a Username:")
        if username:
            file_path = "./config/prompt_username.txt"
            with open(file_path, 'w') as file:
                file.write(username)
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()
        pass
        
    def update_results(self, text_widget, url, paragraph):
        self.after(0, text_widget.insert, tk.END, url + ' ' + paragraph)
        self.update()
        
        
    def open_fileprocess_window():
        root = tk.Tk()
        FileProcessWindow(root)
        root.mainloop()

        
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
            
            
    def delete_conversation_history(self):
        # Delete the conversation history JSON file
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        file_path = f'./history/{username}/{bot_name}_main_conversation_history.json'
        try:
            os.remove(file_path)
            # Reload the script
            self.master.destroy()
            GPT_4_Training()
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
        # Here, we're calling your GPT_4_Training function in a separate thread
        t = threading.Thread(target=self.GPT_4_Text_Extractor_Monologue, args=(a,))
        t.start()
        
        
    def open_fileprocess_window(self):
        fileprocess_window = tk.Toplevel(self)
        fileprocess_window.title("File Processing")

        file_label = tk.Label(fileprocess_window, text="Select a file:")
        file_label.pack()

        results_label = tk.Label(fileprocess_window, text="Files to Process:")
        results_label.pack()

        results_text = tk.Text(fileprocess_window)
        results_text.pack()

        # Function to gather and display the list of files in the destination folders
        def display_existing_files():
            destination_folders = ["./Upload/EPUB", "./Upload/PDF", "./Upload/TXT", "./Upload/SCANS"]
            existing_files = []

            for folder in destination_folders:
                if os.path.exists(folder):
                    files = os.listdir(folder)
                    for file in files:
                        if file != "Finished":
                            existing_files.append(file)

            if existing_files:
                results_text.insert(tk.END, "Existing files:\n")
                for file in existing_files:
                    results_text.insert(tk.END, file + "\n")
            else:
                results_text.insert(tk.END, "No existing files.\n")

            results_text.see(tk.END)

        # Call the function to display existing files when the window is launched
        display_existing_files()

        def select_file():
            filetypes = [
                ("Supported Files", "*.epub *.pdf *.txt *.png *.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
            file_path = filedialog.askopenfilename(filetypes=filetypes)
            if file_path:
                process_file(file_path)

        def process_file(file_path):
            file_name = os.path.basename(file_path)
            extension = os.path.splitext(file_name)[1].lower()

            if extension == ".epub":
                destination_folder = "./Upload/EPUB"
            elif extension == ".pdf":
                destination_folder = "./Upload/PDF"
            elif extension == ".txt":
                destination_folder = "./Upload/TXT"
            elif extension in [".png", ".jpg", ".jpeg"]:
                destination_folder = "./Upload/SCANS"
            else:
                update_results(f"Unsupported file type: {extension}")
                return

            destination_path = os.path.join(destination_folder, file_name)

            try:
                shutil.copy2(file_path, destination_path)
                result_text = f"File '{file_name}' copied to {destination_folder}"
                update_results(result_text)
            except IOError as e:
                error_text = f"Error: {e}"
                update_results(error_text)

        def update_results(text):
            results_text.insert(tk.END, text + "\n")
            results_text.see(tk.END)

        file_button = tk.Button(fileprocess_window, text="Browse", command=select_file)
        file_button.pack()

        search_button = tk.Button(fileprocess_window, text="Process", command=GPT_4_Text_Extract)
        search_button.pack()
        
    def delete_web_history(self):
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        vdb = pinecone.Index("aetherius")
        vdb.delete(filter={"memory_type": "web_scrape"}, namespace=f'Tools_User_{username}_Bot_{bot_name}')
        print('fileprocess has been Deleted')
        pass
        
        
    def delete_fileprocess_db(self):
        # Delete the conversation history JSON file
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        vdb = pinecone.Index("aetherius")
        try:
            vdb.delete(filter={"memory_type": "file_process"}, namespace=f'Tools_User_{username}_Bot_{bot_name}')
            print('File DB has been Deleted')
            self.master.destroy()
            OpenAi_Text_Extractor()
        except:
            print("Fail")
            pass
            
            
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

        self.login_menu = ttk.Combobox(self.top_frame, values=["Login Menu", "----------------------------", "Choose Bot Name", "Choose Username"], state="readonly")
        self.login_menu.pack(side=tk.LEFT, padx=5, pady=5)
        self.login_menu.current(0)
        self.login_menu.bind("<<ComboboxSelected>>", self.handle_login_menu_selection)
        
        
        self.fileprocess_button = tk.Button(self.top_frame, text="Process Files", command=self.open_fileprocess_window, bg=self.button_color, fg=self.text_color)
        self.fileprocess_button.pack(side=tk.LEFT, padx=5, pady=5, ipadx=10)
        
        self.delete_fileprocess_button = tk.Button(self.top_frame, text="Clear File DB", command=self.delete_fileprocess_db, bg=self.button_color, fg=self.text_color)
        self.delete_fileprocess_button.pack(side=tk.LEFT, padx=5, pady=5, ipadx=10)
        
        self.menu = ttk.Combobox(self.top_frame, values=["Config Menu", "----------------------------", "Model Selection", "Edit Font", "Edit Font Size", "Edit Main Prompt", "Edit Secondary Prompt", "Edit Greeting Prompt"], state="readonly")
        self.menu.pack(side=tk.LEFT, padx=5, pady=5)
        self.menu.current(0)
        self.menu.bind("<<ComboboxSelected>>", self.handle_menu_selection)

        self.placeholder_label = tk.Label(self.top_frame, bg=self.background_color)
        self.placeholder_label.pack(side=tk.RIGHT, expand=True, fill=tk.X)

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
        
        
        
        
        
            
    def GPT_4_Text_Extractor_Monologue(self, a):
        vdb = pinecone.Index("aetherius")
        # # Number of Messages before conversation is summarized, higher number, higher api cost. Change to 3 when using GPT 3.5 due to token usage.
        conv_length = 4
        m = multiprocessing.Manager()
        lock = m.Lock()
        print("Type [Clear Memory] to clear saved short-term memory.")
        print("Type [Exit] to exit without saving.")
        tasklist = list()
        conversation = list()
        int_conversation = list()
        conversation2 = list()
        summary = list()
        auto = list()
        payload = list()
        consolidation  = list()
        tasklist_completion = list()
        master_tasklist = list()
        tasklist = list()
        tasklist_log = list()
        memcheck = list()
        memcheck2 = list()
        webcheck = list()
        counter = 0
        counter2 = 0
        mem_counter = 0
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        if not os.path.exists(f'nexus/{bot_name}/{username}/web_scrape_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/web_scrape_memory_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/episodic_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/episodic_memory_nexus')
        if not os.path.exists('Upload/TXT'):
            os.makedirs('Upload/TXT')
        if not os.path.exists('Upload/TXT/Finished'):
            os.makedirs('Upload/TXT/Finished')
        if not os.path.exists('Upload/PDF'):
            os.makedirs('Upload/PDF')
        if not os.path.exists('Upload/PDF/Finished'):
            os.makedirs('Upload/PDF/Finished')
        if not os.path.exists('Upload/EPUB'):
            os.makedirs('Upload/EPUB')
        if not os.path.exists('Upload/EPUB/Finished'):
            os.makedirs('Upload/EPUB/Finished')
        if not os.path.exists(f'nexus/file_process_memory_nexus'):
            os.makedirs(f'nexus/file_process_memory_nexus')
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
        main_prompt = open_file('./config/Chatbot_Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file('./config/Chatbot_Prompts/prompt_secondary.txt')
        greeting_msg = open_file('./config/Chatbot_Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
     #   r = sr.Recognizer()
        while True:
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
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
        #    a = input(f'\n\nUSER: ')
            message_input = a
            vector_input = gpt3_embedding(message_input)
            # # Check for Commands
            # # Check for "Clear Memory"
            if a == 'Clear Memory':
                while True:
                    print('\n\nSYSTEM: Are you sure you would like to delete saved short-term memory?\n        Press Y for yes or N for no.')
                    user_input = input("'Y' or 'N': ")
                    if user_input == 'y':
                        print('Still needs to be converted to new system')
                        vdb.delete(filter={"memory_type": "file_process"}, namespace=f'Tools_User_{username}_Bot_{bot_name}')
                        while True:
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
            # # Check for Exit, summarize the conversation, and then upload to episodic_memories
            conversation.append({'role': 'user', 'content': a})        
            # # Generate Semantic Search Terms
            tasklist.append({'role': 'system', 'content': "You are a task coordinator. Your job is to take user input and create a list of 2-5 inquiries to be used for a semantic database search. Use the format [- 'INQUIRY']."})
            tasklist.append({'role': 'user', 'content': "USER INQUIRY: %s" % a})
            tasklist.append({'role': 'assistant', 'content': "List of Semantic Search Terms: "})
            tasklist_output = chatgpt200_completion(tasklist)
            print(tasklist_output)
            lines = tasklist_output.splitlines()
            db_term = {}
            db_term_result = {}
            db_term_result2 = {}
            tasklist_counter = 0
            # # Split bullet points into separate lines to be used as individual queries during a parallel db search
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        lambda line, _index, conversation, int_conversation: (
                            tasklist_vector := gpt3_embedding(line),
                            db_term.update({_index: tasklist_vector}),
                            results := vdb.query(vector=db_term[_index], filter={
            "memory_type": "explicit_long_term", "user": username}, top_k=3, namespace=f'{bot_name}'),
                            db_term_result.update({_index: load_conversation_explicit_long_term_memory(results)}),
                            results := vdb.query(vector=db_term[_index], filter={
            "memory_type": "implicit_long_term", "user": username}, top_k=2, namespace=f'{bot_name}'),
                            db_term_result2.update({_index: load_conversation_implicit_long_term_memory(results)}),
                            conversation.append({'role': 'assistant', 'content': "MEMORIES: %s" % db_term_result[_index]}),
                            conversation.append({'role': 'assistant', 'content': "MEMORIES: %s" % db_term_result2[_index]}),
                            (
                                int_conversation.append({'role': 'assistant', 'content': "MEMORIES: %s" % db_term_result[_index]}),
                                int_conversation.append({'role': 'assistant', 'content': "MEMORIES: %s" % db_term_result2[_index]})
                            ) if _index < 4 else None,
                        ),
                        line, _index, conversation.copy(), int_conversation.copy()
                    )
                    for _index, line in enumerate(lines) if line.strip()
                ] + [
                    executor.submit(lambda: (
                        vdb.query(vector=vector_input, filter={
            "memory_type": "episodic", "user": username}, top_k=5, namespace=f'{bot_name}'),
                        load_conversation_episodic_memory)
                    ),
                    executor.submit(lambda: (
                        vdb.query(vector=vector_input, filter={
            "memory_type": "explicit_short_term", "user": username}, top_k=8, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}'),
                        load_conversation_explicit_short_term_memory)
                    ),
                    executor.submit(lambda: (
                        vdb.query(vector=vector_input, filter={
            "memory_type": "flashbulb", "user": username}, top_k=2, namespace=f'{bot_name}'),
                        load_conversation_flashbulb_memory)
                    ),
                    executor.submit(lambda: (
                        vdb.query(vector=vector_input, filter={
            "memory_type": "explicit_long_term", "user": username}, top_k=5, namespace=f'{bot_name}'),
                        load_conversation_heuristics)
                    ),
                ]
                try:
                    db_search_1 = futures[len(lines)].result()[1](futures[len(lines)].result()[0])
                    db_search_2 = futures[len(lines) + 1].result()[1](futures[len(lines) + 1].result()[0])
                    db_search_3 = futures[len(lines) + 2].result()[1](futures[len(lines) + 2].result()[0])
                    db_search_4 = futures[len(lines) + 3].result()[1](futures[len(lines) + 3].result()[0])
                except:
                    db_search_1 = 'Database Empty'
                    db_search_2 = 'Database Empty'
                    db_search_3 = 'Database Empty'
                    db_search_4 = 'Database Empty'
           # # # Inner Monologue Generation
            conversation.append({'role': 'assistant', 'content': "MEMORIES: %s;%s;\n\nHEURISTICS: %s;\nUSER MESSAGE: %s;\nBased on %s's memories and the user, %s's message, compose a brief silent soliloquy as %s's inner monologue that reflects on %s's deepest contemplations and emotions in relation to the user's message.\n\nINNER_MONOLOGUE: " % (db_search_1, db_search_2, db_search_3, a, bot_name, username, bot_name, bot_name)})
            output_one = chatgpt250_completion(conversation)
            print('\n\nINNER_MONOLOGUE: %s' % output_one)
            self.master.after(0, self.update_inner_monologue, output_one)

            # After the operations are complete, call the GPT_4_Intuition function in a separate thread
            t = threading.Thread(target=self.GPT_4_Text_Extractor_Intuition, args=(a, vector_input, output_one, int_conversation, tasklist_output))
            t.start()
            return
            
    def update_inner_monologue(self, output_one):
        self.conversation_text.insert(tk.END, f"Inner Monologue: {output_one}\n\n")
        self.conversation_text.yview(tk.END)
            
     
    def GPT_4_Text_Extractor_Intuition(self, a, vector_input, output_one, int_conversation, tasklist_output):
        vdb = pinecone.Index("aetherius")
        # # Number of Messages before conversation is summarized, higher number, higher api cost. Change to 3 when using GPT 3.5 due to token usage.
        conv_length = 4
        m = multiprocessing.Manager()
        lock = m.Lock()
        tasklist = list()
        conversation = list()
        int_conversation = list()
        conversation2 = list()
        summary = list()
        auto = list()
        payload = list()
        consolidation  = list()
        tasklist_completion = list()
        master_tasklist = list()
        tasklist = list()
        tasklist_log = list()
        memcheck = list()
        memcheck2 = list()
        webcheck = list()
        counter = 0
        counter2 = 0
        mem_counter = 0
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        if not os.path.exists(f'nexus/{bot_name}/{username}/web_scrape_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/web_scrape_memory_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/episodic_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/episodic_memory_nexus')
        if not os.path.exists('Upload/TXT'):
            os.makedirs('Upload/TXT')
        if not os.path.exists('Upload/TXT/Finished'):
            os.makedirs('Upload/TXT/Finished')
        if not os.path.exists('Upload/PDF'):
            os.makedirs('Upload/PDF')
        if not os.path.exists('Upload/PDF/Finished'):
            os.makedirs('Upload/PDF/Finished')
        if not os.path.exists('Upload/EPUB'):
            os.makedirs('Upload/EPUB')
        if not os.path.exists('Upload/EPUB/Finished'):
            os.makedirs('Upload/EPUB/Finished')
        if not os.path.exists(f'nexus/file_process_memory_nexus'):
            os.makedirs(f'nexus/file_process_memory_nexus')
        main_prompt = open_file('./config/Chatbot_Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file('./config/Chatbot_Prompts/prompt_secondary.txt')
        greeting_msg = open_file('./config/Chatbot_Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
     #   r = sr.Recognizer()
        while True:
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            message = output_one
            vector_monologue = gpt3_embedding('Inner Monologue: ' + message)
            tasklist_new = tasklist_output
            # # Clear Conversation List
            conversation.clear()
            # # Memory DB Search
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future1 = executor.submit(vdb.query, vector=vector_monologue, filter={
            "memory_type": "episodic", "user": username}, top_k=5, namespace=f'{bot_name}')
                future2 = executor.submit(vdb.query, vector=vector_input, filter={
            "memory_type": "explicit_short_term", "user": username}, top_k=10, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                future3 = executor.submit(vdb.query, vector=vector_monologue, filter={
            "memory_type": "flashbulb", "user": username}, top_k=2, namespace=f'{bot_name}')
                future4 = executor.submit(vdb.query, vector=vector_monologue, filter={
            "memory_type": "heuristics", "user": username}, top_k=3, namespace=f'{bot_name}')
                try:
                    db_search_4 = load_conversation_episodic_memory(future1.result())
                    db_search_5 = load_conversation_explicit_short_term_memory(future2.result())
                    db_search_12 = load_conversation_flashbulb_memory(future3.result())
                    db_search_13 = load_conversation_heuristics(future4.result())
                except:
                    db_search_4 = 'Database Empty'
                    db_search_5 = 'Database Empty'
                    db_search_12 = 'Database Empty'
                    db_search_13 = 'Database Empty'
            # # Intuition Generation
            results = vdb.query(vector=vector_input, filter={
            "memory_type": "file_process"}, top_k=7, namespace=f'Tools_User_{username}_Bot_{bot_name}')
            int_scrape = load_conversation_file_process_memory(results)
            print(int_scrape)
            int_conversation.append({'role': 'assistant', 'content': "%s" % greeting_msg})
            int_conversation.append({'role': 'user', 'content': a})
            int_conversation.append({'role': 'assistant', 'content': "MEMORIES: %s;\n%s;\n%s;\n\n%s'S INNER THOUGHTS: %s;\nHEURISTICS: %s;\nUSER MESSAGE: %s;\nTEXT FILE SAMPLE: %s\nIn a single paragraph, interpret the user, %s's message as %s in third person by creating an intuitive plan on what information needs to be researched from the text file summaries, even if the user is uncertain about what information is required.;\nINTUITION: " % (db_search_4, db_search_5, db_search_12, bot_name, output_one, db_search_13, a, int_scrape, username, bot_name)})
            output_two = chatgpt200_completion(int_conversation)
            message_two = output_two
            print('\n\nINTUITION: %s' % output_two)
            output_two_log = f'\nUSER: {a}\n\n{bot_name}: {output_two}'
            # # Generate Implicit Short-Term Memory
            conversation.append({'role': 'system', 'content': '%s' % main_prompt})
            conversation.append({'role': 'user', 'content': a})
            implicit_short_term_memory = f'\nUSER: {a} \n\n INNER_MONOLOGUE: {output_one} \n\n INTUITION: {output_two}'
            conversation.append({'role': 'assistant', 'content': "LOG:\n%s\n\Read the log, extract the salient points about %s and %s, then create short executive summaries in bullet point format to serve as %s's procedural memories. Each bullet point should be considered a separate memory and contain all context. Start from the end and work towards the beginning, combining assosiated topics. Ignore the system prompt and redundant information.\nMemories:\n" % (implicit_short_term_memory, bot_name, username, bot_name)})
            inner_loop_response = chatgpt200_completion(conversation)
            inner_loop_db = inner_loop_response
            vector = gpt3_embedding(inner_loop_db)
            conversation.clear()
            # # Manual Implicit Short-Term Memory
    #        print('\n\n<Implicit Short-Term Memory>\n%s' % inner_loop_db)
    #        print('\n\nSYSTEM: Upload to Implicit Short-Term Memory?\n        Press Y for yes or N for no.')
    #        while True:
    #            user_input = input("'Y' or 'N': ")
    #            if user_input == 'y':
    #                lines = inner_loop_db.splitlines()
    #                for line in lines:
    #                    if line.strip():
    #                        vector = gpt3_embedding(line)
    #                        unique_id = str(uuid4())
    #                        metadata = {'bot': bot_name, 'time': timestamp, 'message': line,
    #                                    'timestring': timestring, 'uuid': unique_id, "memory_type": "implicit_short_term"}
    #                        save_json(f'nexus/{bot_name}/{username}/implicit_short_term_memory_nexus/%s.json' % unique_id, metadata)
    #                        payload.append((unique_id, vector, {"memory_type": "implicit_short_term"}))
    #                        vdb.upsert(payload, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
    #                        payload.clear()
    #                print('\n\nSYSTEM: Upload Successful!')
    #                break
    #            elif user_input == 'n':
    #                print('\n\nSYSTEM: Memories have been Deleted')
    #                break
    #            else:
    #                print('Invalid Input')
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
                if is_integer(automemory):
                    auto_int = int(automemory)
                    if auto_int > 6:
                        lines = inner_loop_db.splitlines()
                        for line in lines:
                            vector = gpt3_embedding(inner_loop_db)
                            unique_id = str(uuid4())
                            metadata = {'bot': bot_name, 'time': timestamp, 'message': inner_loop_db,
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
            self.master.after(0, self.update_tasklist_intuition, output_two)

            # After the operations are complete, call the response generation function in a separate thread
            t = threading.Thread(target=self.GPT_4_Extractor_Response, args=(a, vector_input, vector_monologue, output_one, output_two, tasklist_new))
            t.start()
            return 

    def update_tasklist_intuition(self, output_two):
        self.conversation_text.insert(tk.END, f"Intuition: {output_two}\n\n")
        self.conversation_text.yview(tk.END)



    def GPT_4_Extractor_Response(self, a, vector_input, vector_monologue, output_one, output_two, tasklist_new):
        vdb = pinecone.Index("aetherius")
        # # Number of Messages before conversation is summarized, higher number, higher api cost. Change to 3 when using GPT 3.5 due to token usage.
        conv_length = 4
        m = multiprocessing.Manager()
        lock = m.Lock()
        tasklist = list()
        conversation = list()
        int_conversation = list()
        conversation2 = list()
        summary = list()
        auto = list()
        payload = list()
        consolidation  = list()
        tasklist_completion = list()
        master_tasklist = list()
        tasklist = list()
        tasklist_log = list()
        memcheck = list()
        memcheck2 = list()
        webcheck = list()
        counter = 0
        counter2 = 0
        mem_counter = 0
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        if not os.path.exists(f'nexus/{bot_name}/{username}/web_scrape_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/web_scrape_memory_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/episodic_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/episodic_memory_nexus')
        if not os.path.exists('Upload/TXT'):
            os.makedirs('Upload/TXT')
        if not os.path.exists('Upload/TXT/Finished'):
            os.makedirs('Upload/TXT/Finished')
        if not os.path.exists('Upload/PDF'):
            os.makedirs('Upload/PDF')
        if not os.path.exists('Upload/PDF/Finished'):
            os.makedirs('Upload/PDF/Finished')
        if not os.path.exists('Upload/EPUB'):
            os.makedirs('Upload/EPUB')
        if not os.path.exists('Upload/EPUB/Finished'):
            os.makedirs('Upload/EPUB/Finished')
        if not os.path.exists(f'nexus/file_process_memory_nexus'):
            os.makedirs(f'nexus/file_process_memory_nexus')
        main_prompt = open_file('./config/Chatbot_Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file('./config/Chatbot_Prompts/prompt_secondary.txt')
        greeting_msg = open_file('./config/Chatbot_Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
     #   r = sr.Recognizer()
        while True:
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            tasklist_output = tasklist_new
            # # Test for basic Autonomous Tasklist Generation and Task Completion
            master_tasklist.append({'role': 'system', 'content': "You are a stateless task list coordinator for %s an autonomous Ai chatbot. Your job is to combine the user's input and the user facing chatbots intuitive action plan, then transform it into a list of independent research queries that can be executed by separate AI agents in a cluster computing environment. The other asynchronous Ai agents are also stateless and cannot communicate with each other or the user during task execution, they do however have access to %s's memories. Exclude tasks involving final product production, hallucinations, user communication, or checking work with other agents. Respond using the following format: '- [task]'" % (bot_name, bot_name)})
            master_tasklist.append({'role': 'user', 'content': "USER FACING CHATBOT'S INTUITIVE ACTION PLAN:\n%s" % output_two})
            master_tasklist.append({'role': 'user', 'content': "USER INQUIRY:\n%s" % a})
            master_tasklist.append({'role': 'user', 'content': "SEMANTICALLY SIMILAR INQUIRIES:\n%s" % tasklist_output})
            master_tasklist.append({'role': 'assistant', 'content': "TASK LIST:"})
            master_tasklist_output = chatgpt_tasklist_completion(master_tasklist)
            print(master_tasklist_output)
            tasklist_completion.append({'role': 'system', 'content': f"{main_prompt}"})
            tasklist_completion.append({'role': 'assistant', 'content': f"You are the final response module of the cluster compute Ai-Chatbot {bot_name}. Your job is to take the completed task list, and give a verbose response to the end user in accordance with their initial request."})
            tasklist_completion.append({'role': 'user', 'content': "%s" % master_tasklist_output})
            task = {}
            task_result = {}
            task_result2 = {}
            task_counter = 1
            # # Split bullet points into separate lines to be used as individual queries
            lines = master_tasklist_output.splitlines()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        lambda line, task_counter, conversation, memcheck, memcheck2, webcheck, tasklist_completion: (
                            tasklist_completion.append({'role': 'user', 'content': f"ASSIGNED TASK:\n{line}"}),
                            conversation.append({'role': 'system', 'content': "You are a sub-agent for {bot_name}, an Autonomous Ai-Chatbot. You are one of many agents in a chain. You are to take the given task and complete it in its entirety. Be Verbose and take other tasks into account when formulating your answer."}),
                            conversation.append({'role': 'assistant', 'content': "{bot_name}'s INNER MONOLOGUE: {output_one}"}),
                            conversation.append({'role': 'user', 'content': f"Task list:\n{master_tasklist_output}"}),
                            conversation.append({'role': 'assistant', 'content': "Bot: I have studied the given tasklist.  What is my assigned task?"}),
                            conversation.append({'role': 'user', 'content': f"Bot Assigned task: {line}"}),
                                # # DB Yes No Tool
                            memcheck.append({'role': 'system', 'content': f"You are a sub-agent for {bot_name}, an Autonomous Ai-Chatbot. You are one of many agents in a chain. Your task is to decide if the user's input requires {bot_name}'s past memories to complete. Any information pertaining to the user, {bot_name}, or the main bot, {bot_name} should be searched for.  If past memories are needed, print: YES.  If they are not needed, print: NO."}),
                            memcheck.append({'role': 'user', 'content': f"{bot_name}'s Inner Monologue: %s"}),
                            memcheck.append({'role': 'user', 'content': f"{bot_name}'s Intuition: %s"}),
                            memcheck.append({'role': 'user', 'content': "//LIST OF EXAMPLES:"}),
                            memcheck.append({'role': 'user', 'content': "Research ways to identify user needs and interests"}),
                            memcheck.append({'role': 'assistant', 'content': "YES"}),
                            memcheck.append({'role': 'user', 'content': "Research common themes in the book Faust."}),
                            memcheck.append({'role': 'assistant', 'content': "NO"}),
                            memcheck.append({'role': 'user', 'content': f"Search {bot_name}'s memory for context."}),
                            memcheck.append({'role': 'assistant', 'content': "YES"}),
                            memcheck.append({'role': 'user', 'content': "END OF EXAMPLE LIST//"}),
                            memcheck.append({'role': 'assistant', 'content': "{bot_name} REINITIALIZATION: Your task is to decide if the user's input requires %s's past memories to complete. If past memories are needed, print: YES.  If they are not needed, print: NO."}),
                            memcheck.append({'role': 'user', 'content': "What would you like to talk about?"}),
                            memcheck.append({'role': 'assistant', 'content': "YES"}),
                                # # DB Selector Tool
                            memcheck2.append({'role': 'system', 'content': f"You are a sub-module for {bot_name}, an Autonomous Ai-Chatbot. You are one of many agents in a chain. Your task is to decide which database needs to be queried in relation to a user's input. The databases are representitive of different types of memories. Only choose a single database to query. Respond in this format: RESPONSE"}),
                            memcheck2.append({'role': 'assistant', 'content': f"{bot_name}'s INNER_MONOLOGUE: {output_one}"}),
                            memcheck2.append({'role': 'user', 'content': "//LIST OF MEMORY TYPE NAMES:"}),
                            memcheck2.append({'role': 'user', 'content': "EPISODIC: These are memories of personal experiences and specific events that occur in a particular time and place. These memories often include contextual details, such as emotions, sensations, and the sequence of events."}),
                            memcheck2.append({'role': 'user', 'content': "FLASHBULB: Flashbulb memories are vivid, detailed, and long-lasting memories of highly emotional or significant events, such as learning about a major news event or experiencing a personal tragedy."}),
                            memcheck2.append({'role': 'user', 'content': "IMPLICIT LONG TERM: Unconscious memory not easily verbalized, including procedural memory (skills and habits), classical conditioning (associations between stimuli and reflexive responses), and priming (unconscious activation of specific associations)."}),
                            memcheck2.append({'role': 'user', 'content': "EXPLICIT LONG TERM: Conscious recollections of facts and events, including episodic memory (personal experiences and specific events) and semantic memory (general knowledge, concepts, and facts)."}),
                            memcheck2.append({'role': 'user', 'content': "END OF LIST//\n\n//EXAMPLE QUERIES:"}),
                            memcheck2.append({'role': 'user', 'content': "Research common topics discussed with users who start a conversation with 'hello'"}),
                            memcheck2.append({'role': 'assistant', 'content': "EPISODIC MEMORY"}),
                            memcheck2.append({'role': 'user', 'content': "Create a research paper on the book Faust."}),
                            memcheck2.append({'role': 'assistant', 'content': "NO MEMORIES NEEDED"}),
                            memcheck2.append({'role': 'user', 'content': "Tell me about your deepest desires."}),
                            memcheck2.append({'role': 'assistant', 'content': "FLASHBULB"}),
                            memcheck2.append({'role': 'user', 'content': "END OF EXAMPLE QUERIES//\n\n//BEGIN JOB:"}),
                            memcheck2.append({'role': 'user', 'content': "JOB: Your task is to decide which database needs to be queried in relation to a user's input. The databases are representitive of different types of memories. Only choose a single database to query. Respond in this format: RESPONSE"}),
                                # # Web Search Tool
                         #       webcheck.append({'role': 'system', 'content': f"You are a sub-module for an Autonomous Ai-Chatbot. You are one of many agents in a chain. Your task is to decide if a web-search is needed in order to complete the given task. Only recent or niche information needs to be searched. Do not search for any information pertaining to the user, {bot_name}, or the main bot, {bot_name}.   If a websearch is needed, print: YES.  If a web-search is not needed, print: NO."}),
                        #        webcheck.append({'role': 'user', 'content': "Hello, how are you today?"}),
                        #        webcheck.append({'role': 'assistant', 'content': "NO"}),
                                # # Check if websearch is needed
                        #        webcheck.append({'role': 'user', 'content': f"{line}"}),
                        #        web1 := chatgptyesno_completion(webcheck),
                        #        table := google_search(line) if web1 =='YES' else fail(),
                            #    table := google_search(line, my_api_key, my_cse_id) if web1 == 'YES' else fail(),
                            table := search_file_process_db(line),
                            #    google_search(line, my_api_key, my_cse_id),
                            # # Check if DB search is needed
                            memcheck.append({'role': 'user', 'content': f"{line}"}),
                            mem1 := chatgptyesno_completion(memcheck),
                            # # Go to conditional for choosing DB Name
                            memcheck2.append({'role': 'user', 'content': f"{line}"}),
                            mem2 := chatgptselector_completion(memcheck2) if mem1 == 'YES' else fail(),
                            line_vec := gpt3_embedding(line),    #EPISODIC, FLASHBULB, IMPLICIT LONG TERM, EXPLICIT LONG TERM
                            memories := (search_episodic_db(line_vec) if mem2 == 'EPISODIC' else
                                         search_implicit_db(line_vec) if mem2 == 'IMPLICIT LONG TERM' else
                                         search_flashbulb_db(line_vec) if mem2 == 'FLASHBULB' else
                                         search_explicit_db(line_vec) if mem2 == 'EXPLICIT LONG TERM' else
                                         fail()),
                            conversation.append({'role': 'assistant', 'content': "TEXT FILE SEARCH: %s" % table}),
                            conversation.append({'role': 'user', 'content': "Bot %s Task Reinitialization: %s" % (task_counter, line)}),
                            conversation.append({'role': 'user', 'content': "SYSTEM: Try to relate the bot's task to the given text articles."}),
                            conversation.append({'role': 'assistant', 'content': "Bot %s's Response:" % task_counter}),
                            task_completion := chatgpt35_completion(conversation),
                            #chatgpt35_completion(conversation),
                            #  conversation.clear(),
                            tasklist_completion.append({'role': 'assistant', 'content': "TEXT FILE SEARCH: %s" % table}),
                            tasklist_completion.append({'role': 'assistant', 'content': "Research for Task Completion: %s" % memories}),
                            tasklist_completion.append({'role': 'assistant', 'content': "COMPLETED TASK:\n%s" % task_completion}),
                            tasklist_log.append({'role': 'user', 'content': "ASSIGNED TASK:\n%s\n\n" % line}),
                            tasklist_log.append({'role': 'assistant', 'content': "COMPLETED TASK:\n%s\n\n" % memories}),
                            print(line),
                            print(memories),
                        #     print(table),
                            print(task_completion),
                    #        print(task_completion),
                        ) if line != "None" else tasklist_completion,
                        line, task_counter, memcheck.copy(), memcheck2.copy(), webcheck.copy(), conversation.copy(), []
                    )
                    for task_counter, line in enumerate(lines)
                ]
                tasklist_completion.append({'role': 'assistant', 'content': f"{bot_name}'s INNER_MONOLOGUE: {output_one}"})
                tasklist_completion.append({'role': 'user', 'content': f"{bot_name}'s INTUITION: {output_two}"})
                tasklist_completion.append({'role': 'user', 'content': f"Take the given set of tasks and completed responses and transmute them into a verbose response for {bot_name}, the end user in accordance with their request. The end user is both unaware and unable to see any of your research. User's initial request: {a}"})
                print('\n\nGenerating Final Output...')
                response_two = chatgpt_tasklist_completion(tasklist_completion)
                print('\nFINAL OUTPUT:\n%s' % response_two)
                complete_message = f'\nUSER: {a}\n\nINNER_MONOLOGUE: {output_one}\n\nINTUITION: {output_two}\n\n{bot_name}: {tasklist_log}\n\nFINAL OUTPUT: {response_two}'
                filename = '%s_chat.txt' % timestamp
                save_file('logs/complete_chat_logs/%s' % filename, complete_message)
                conversation.clear()
                int_conversation.clear()
                conversation2.clear()
                tasklist_completion.clear()
                master_tasklist.clear()
                tasklist.clear()
                tasklist_log.clear()
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
            db_msg = f'\nUSER: {a} \n\n INNER_MONOLOGUE: {output_one} \n\n {bot_name}: {response_two}'
            summary.append({'role': 'user', 'content': "LOG:\n%s\n\Read the log and create short executive summaries in bullet point format to serve as %s's explicit memories. Each bullet point should be considered a separate memory and contain all context. Start from the end and work towards the beginning, combining assosiated topics.\nMemories:\n" % (db_msg, bot_name)})
            db_upload = chatgptsummary_completion(summary)
            db_upsert = db_upload
            # # Manual Short-Term Memory DB Upload Confirmation
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
            auto.append({'role': 'assistant', 'content': "Inner Monologue: %s\nIntuition: %s" % (output_one, output_two)})
            auto.append({'role': 'assistant', 'content': "Thoughts on input: I will now review the user's message and my reply, rating if whether my thoughts are both pertinent to the user's inquiry and my growth with a number on a scale of 1-10. I will now give my response in digit form for an integer only input: "})
            auto_int = None
            while auto_int is None:
                automemory = chatgptyesno_completion(auto)
                if is_integer(automemory):
                    auto_int = int(automemory)
                    if auto_int > 6:
                        lines = db_upsert.splitlines()
                        for line in lines:
                            vector = gpt3_embedding(db_upsert)
                            unique_id = str(uuid4())
                            metadata = {'bot': bot_name, 'time': timestamp, 'message': db_upsert,
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
            conversation.clear()
            int_conversation.clear()
            summary.clear()
            counter += 1
            self.conversation_text.insert(tk.END, f"Response: {response_two}\n\n")
            self.conversation_text.yview(tk.END)
            self.user_input.delete(0, tk.END)
            self.user_input.focus()
            self.user_input.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.thinking_label.pack_forget()
            self.user_input.delete(0, tk.END)
            self.bind_enter_key()
            return
            
            
    def GPT_4_Extractor_Memories(self, a, vector_input, vector_monologue, output_one, output_two, tasklist_new):
        vdb = pinecone.Index("aetherius")
        # # Number of Messages before conversation is summarized, higher number, higher api cost. Change to 3 when using GPT 3.5 due to token usage.
        conv_length = 4
        m = multiprocessing.Manager()
        lock = m.Lock()
        print("Type [Clear Memory] to clear saved short-term memory.")
        print("Type [Exit] to exit without saving.")
        tasklist = list()
        conversation = list()
        int_conversation = list()
        conversation2 = list()
        summary = list()
        auto = list()
        payload = list()
        consolidation  = list()
        tasklist_completion = list()
        master_tasklist = list()
        tasklist = list()
        tasklist_log = list()
        memcheck = list()
        memcheck2 = list()
        webcheck = list()
        counter = 0
        counter2 = 0
        mem_counter = 0
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        if not os.path.exists(f'nexus/{bot_name}/{username}/web_scrape_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/web_scrape_memory_nexus')
        if not os.path.exists(f'nexus/{bot_name}/{username}/episodic_memory_nexus'):
            os.makedirs(f'nexus/{bot_name}/{username}/episodic_memory_nexus')
        if not os.path.exists('Upload/TXT'):
            os.makedirs('Upload/TXT')
        if not os.path.exists('Upload/TXT/Finished'):
            os.makedirs('Upload/TXT/Finished')
        if not os.path.exists('Upload/PDF'):
            os.makedirs('Upload/PDF')
        if not os.path.exists('Upload/PDF/Finished'):
            os.makedirs('Upload/PDF/Finished')
        if not os.path.exists('Upload/EPUB'):
            os.makedirs('Upload/EPUB')
        if not os.path.exists('Upload/EPUB/Finished'):
            os.makedirs('Upload/EPUB/Finished')
        if not os.path.exists(f'nexus/file_process_memory_nexus'):
            os.makedirs(f'nexus/file_process_memory_nexus')
        main_prompt = open_file('./config/Chatbot_Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file('./config/Chatbot_Prompts/prompt_secondary.txt')
        greeting_msg = open_file('./config/Chatbot_Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
     #   r = sr.Recognizer()
        while True:  
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            print('Generating Episodic Memories')
            conversation.append({'role': 'system', 'content': f"You are a sub-module of {bot_name}, an autonomous AI entity. Your function is to process the user, {username}'s message, comprehend {bot_name}'s internal workings, and decode {bot_name}'s final response to construct a concise third-person autobiographical narrative memory of the conversation in a single sentence. This autobiographical memory should portray an accurate and personalized account of {bot_name}'s interactions with {username}, focusing on the most significant and experiential details related to {bot_name} or {username}, without omitting any crucial context or emotions."})
            conversation.append({'role': 'user', 'content': f"USER's INQUIRY: {a}"})
            conversation.append({'role': 'user', 'content': f"{bot_name}'s INNER MONOLOGUE: {output_one}"})
            conversation.append({'role': 'user', 'content': f"{bot_name}'s FINAL RESPONSE: {response_two}"})
            conversation.append({'role': 'assistant', 'content': f"I will now extract an episodic memory based on the given conversation: "})
            conv_summary = chatgptsummary_completion(conversation)
        #    print(timestring + '-' + conv_summary)
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
                im_flash = gpt3_embedding(flash_db)
                results = vdb.query(vector=im_flash, filter={
            "memory_type": "implicit_long_term", "user": username}, top_k=10, namespace=f'{bot_name}') 
                flash_db1 = load_conversation_implicit_long_term_memory(results) 
                # # Generate Implicit Short-Term Memory
                consolidation.append({'role': 'system', 'content': 'You are a data extractor. Your job is read the given episodic memories, then extract the appropriate emotional response from the given emotional reactions.  You will then combine them into a single memory.'})
                consolidation.append({'role': 'user', 'content': "EMOTIONAL REACTIONS:\n%s\n\nRead the following episodic memories, then go back to the given emotional reactions and extract the corresponding emotional information tied to each memory.\nEPISODIC MEMORIES: %s" % (flash_db, flash_db1)})
                consolidation.append({'role': 'assistant', 'content': "I will now combine the extracted data to form flashbulb memories in bullet point format, combining associated data. I will only include memories with a strong emotion attached, excluding redundant or irrelevant information."})
                consolidation.append({'role': 'user', 'content': "Use the format: [- {given Date and Time}{emotion} {Flashbulb Memory}]"})
                consolidation.append({'role': 'assistant', 'content': "I will now create %s's flashbulb memories using the given format: " % bot_name})
                flash_response = chatgptconsolidation_completion(consolidation)
                memories = results
                lines = flash_response.splitlines()
                for line in lines:
                    if line.strip():
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
            if namespace_name in namespace_stats and namespace_stats[namespace_name]['vector_count'] > 30:
                consolidation.clear()
                print(f"{namespace_name} has 30 or more entries, starting memory consolidation.")
                results = vdb.query(vector=vector_input, filter={"memory_type": "explicit_short_term"}, top_k=25, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                memory_consol_db = load_conversation_explicit_short_term_memory(results)
                consolidation.append({'role': 'system', 'content': "%s" % main_prompt})
                consolidation.append({'role': 'assistant', 'content': "LOG:\n%s\n\nRead the Log and consolidate the different topics into executive summaries. Each summary should contain the entire context of the memory. Follow the format [- Executive Summary]." % memory_consol_db})
                memory_consol = chatgptconsolidation_completion(consolidation)
                lines = memory_consol.splitlines()
                for line in lines:
                    if line.strip():
                #    print(timestring + line)
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
                    results = vdb.query(vector=vector_input, filter={"memory_type": "implicit_short_term"}, top_k=20, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
                    memory_consol_db2 = load_conversation_implicit_short_term_memory(results)
                    consolidation.append({'role': 'system', 'content': "%s" % main_prompt})
                    consolidation.append({'role': 'assistant', 'content': "LOG:\n%s\n\nRead the Log and consolidate the different topics into executive summaries to serve as %s's implicit memories. Each summary should contain the entire context of the memory. Follow the format: [-{tag} {Executive Summary}]." % (memory_consol_db2, bot_name)})
                    memory_consol2 = chatgptconsolidation_completion(consolidation)
                    consolidation.clear()
                    print('Finished.\nRemoving Redundant Memories.')
                    vector_sum = gpt3_embedding(memory_consol2)
                    results = vdb.query(vector=vector_sum, filter={"memory_type": "implicit_long_term", "user": username}, top_k=8, namespace=f'{bot_name}')
                    memory_consol_db3 = load_conversation_implicit_long_term_memory(results)
                    consolidation.append({'role': 'system', 'content': "%s" % main_prompt})
                    consolidation.append({'role': 'system', 'content': "IMPLICIT LONG TERM MEMORY: %s\n\nIMPLICIT SHORT TERM MEMORY: %s\n\nRemove any duplicate information from your Implicit Short Term memory that is already found in your Long Term Memory. Then consolidate similar topics into executive summaries. Each summary should contain the entire context of the memory. Use the following format: [- {emotion} {Memory}]" % (memory_consol_db3, memory_consol_db2)})
                    memory_consol3 = chatgptconsolidation_completion(consolidation)
                    lines = memory_consol3.splitlines()
                    for line in lines:
                        if line.strip():
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
                    ids_to_delete = [m['id'] for m in results['matches']]
                    consolidation.append({'role': 'system', 'content': "%s" % main_prompt})
                    consolidation.append({'role': 'assistant', 'content': "LOG:\n%s\n\nRead the Log and consolidate the different memories into executive summaries in a process allegorical to associative processing. Each summary should contain the entire context of the memory. Follow the format: [-{tag} {Memory}]" % memory_consol_db1})
                    memory_consol = chatgptconsolidation_completion(consolidation)
                    memories = results
                    lines = memory_consol.splitlines()
                    for line in lines:
                        if line.strip():
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
                    consolidation.append({'role': 'user', 'content': "%s's Memories:\n%s" % (bot_name, consol_search)})
                    consolidation.append({'role': 'assistant', 'content': "Semantic Search Query: "})
                    consol_search_term = chatgpt200_completion(consolidation)
                    consol_vector = gpt3_embedding(consol_search_term)
                    results = vdb.query(vector=consol_vector, filter={"memory_type": "explicit_long_term", "user": username}, top_k=10, namespace=f'{bot_name}')
                    memory_consol_db2 = load_conversation_explicit_long_term_memory(results)
                    ids_to_delete2 = [m['id'] for m in results['matches']]
                    consolidation.clear()
                    consolidation.append({'role': 'system', 'content': "%s" % main_prompt})
                    consolidation.append({'role': 'assistant', 'content': "LOG:\n%s\n\nRead the Log and consolidate the different memories into executive summaries in a process allegorical to associative processing. Each summary should contain the entire context of the memory. Follow the format: [-{tag} Memory]" % memory_consol_db2})
                    memory_consol2 = chatgptconsolidation_completion(consolidation)
                    memories = results
                    lines = memory_consol2.splitlines()
                    for line in lines:
                        if line.strip():
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
            return

            
            
            
            
            
            
  
def set_dark_ancient_theme():
    background_color = "#2B303A"  # Dark blue-gray
    foreground_color = "#FDF7E3"  # Pale yellow
    button_color = "#415A77"  # Dark grayish blue
    text_color = 'white'

    return background_color, foreground_color, button_color, text_color
  
  
  

def chatgptselector_completion(messages, model="gpt-3.5-turbo", temp=0.2):
    max_retry = 7
    retry = 0
    m = multiprocessing.Manager()
    lock = m.Lock()
    with lock:
        try:
            response = openai.ChatCompletion.create(model=model, messages=messages, max_tokens=4)
            text = response['choices'][0]['message']['content']
            temperature = temp
        #    filename = '%s_chat.txt' % time()
        #    if not os.path.exists('chat_logs'):
        #        os.makedirs('chat_logs')
        #    save_file('chat_logs/%s' % filename, str(messages) + '\n\n==========\n\n' + text)
            print(text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                print(f"Exiting due to an error in ChatGPT: {oops}")
                exit(1)
            print(f'Error communicating with OpenAI: "{oops}" - Retrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)

    
def search_implicit_db(line_vec):
    m = multiprocessing.Manager()
    lock = m.Lock()
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    vdb = pinecone.Index("aetherius")
    try:
        with lock:
            print('implicit')
            results = vdb.query(vector=line_vec, filter={"memory_type": "implicit_long_term", "user": username}, top_k=7, namespace=f'{bot_name}')
            memories1 = load_conversation_implicit_long_term_memory(results)
            results = vdb.query(vector=line_vec, filter={"memory_type": "implicit_short_term"}, top_k=5, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
            memories2 = load_conversation_implicit_short_term_memory(results)
            memories = f'{memories1}\n{memories2}'
            print(memories)
            return memories
    except Exception as e:
        print(e)
        memories = "Error"
        return memories
    
    
def search_episodic_db(line_vec):
    m = multiprocessing.Manager()
    lock = m.Lock()
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    vdb = pinecone.Index("aetherius")
    try:
        with lock:
            results = vdb.query(vector=line_vec, filter={
            "memory_type": "episodic", "user": username}, top_k=5, namespace=f'{bot_name}')
            memories = load_conversation_episodic_memory(results)
            return memories
    except Exception as e:
        print(e)
        memories = "Error"
        return memories
            
    
def search_flashbulb_db(line_vec):
    m = multiprocessing.Manager()
    lock = m.Lock()
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    vdb = pinecone.Index("aetherius")
    try:
        with lock:
            results = vdb.query(vector=line_vec, filter={
            "memory_type": "flashbulb", "user": username}, top_k=5, namespace=f'{bot_name}')
            memories = load_conversation_flashbulb_memory(results)
            return memories
    except Exception as e:
        print(e)
        memories = "Error"
        return memories 
    
    
def search_explicit_db(line_vec):
    m = multiprocessing.Manager()
    lock = m.Lock()
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    vdb = pinecone.Index("aetherius")
    try:
        with lock:
            print('explicit')
            results = vdb.query(vector=line_vec, filter={"memory_type": "explicit_long_term", "user": username}, top_k=5, namespace=f'{bot_name}')
            memories1 = load_conversation_explicit_long_term_memory(results)
            results = vdb.query(vector=line_vec, filter={"memory_type": "explicit_short_term"}, top_k=5, namespace=f'short_term_memory_User_{username}_Bot_{bot_name}')
            memories2 = load_conversation_explicit_short_term_memory(results)
            memories = f'{memories1}\n{memories2}'
            print(memories)
            return memories
    except Exception as e:
        print(e)
        memories = "Error"
        return memories   
        
        
def split_into_chunks(text, chunk_size):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def chunk_text(text, chunk_size, overlap):
    chunks = []
    start = 0
    end = chunk_size
    while end <= len(text):
        chunks.append(text[start:end])
        start += chunk_size - overlap
        end += chunk_size - overlap
    if end > len(text):
        chunks.append(text[start:])
    return chunks
    
def open_image_file(image_path):
    try:
        img = Image.open(image_path)
        return img
    except IOError:
        print("Error: File not found or the file format is not supported.")
        return None

def save_text_to_file(text, save_path):
    try:
        with open(save_path, 'w') as file:
            file.write(text)
    except Exception as e:
        print(f"Error occurred while saving text to file: {str(e)}")


def chunk_text_from_file(file_path, chunk_size=1500, overlap=300):
    try:
        print("Reading given file, please wait...")
        username = open_file('./config/prompt_username.txt')
        bot_name = open_file('./config/prompt_bot_name.txt')
        vdb = pinecone.Index("aetherius")
        pytesseract.pytesseract.tesseract_cmd = '.\\Tesseract-ocr\\tesseract.exe'
        textemp = None
        file_extension = os.path.splitext(file_path)[1].lower() 
        if file_extension == '.txt':
            with open(file_path, 'r') as file:
                texttemp = file.read().replace('\n', ' ').replace('\r', '')
        elif file_extension == '.pdf':
            with open(file_path, 'rb') as file:
                pdf = PdfReader(file)
                texttemp = " ".join(page.extract_text() for page in pdf.pages)
        elif file_extension == '.epub':
            book = epub.read_epub(file_path)
            texts = []
            for item in book.get_items_of_type(9):  # type 9 is XHTML
                soup = BeautifulSoup(item.content, 'html.parser')
                texts.append(soup.get_text())
            texttemp = ' '.join(texts)
        elif file_extension in ['.png', '.jpg', '.jpeg']:
            image = open_image_file(file_path)
            if image is not None:
                texttemp = pytesseract.image_to_string(image).replace('\n', ' ').replace('\r', '')
                # Save OCR output to raw text file
                save_path = './Upload/SCANS/Finished/Raw/' + os.path.basename(file_path) + '.txt'
                save_text_to_file(texttemp, save_path)
        else:
            print(f"Unsupported file type: {file_extension}")
            return []
        texttemp = '\n'.join(line for line in texttemp.splitlines() if line.strip())
        chunks = chunk_text(texttemp, chunk_size, overlap)
        filelist = list()
        for chunk in chunks:
            filesum = list()
            filesum.append({'role': 'system', 'content': "You are a Data Summarizer sub-module, responsible for processing text data from files. Your role includes identifying and highlighting significant or factual information. Extraneous data should be discarded, and only essential details must be returned. Stick to the data provided; do not infer or generalize.  Convert lists into a continuous text summary to maintain this format. Present your responses in a Running Text format using the following pattern: [SEMANTIC QUESTION TAG:SUMMARY]. Note that the semantic question tag should be a question that corresponds to the paired information within the summary. Always provide the two together without linebreaks."})
            filesum.append({'role': 'user', 'content': f"TEXT CHUNK: {chunk}"})
            text = chatgpt35_completion(filesum)
            paragraphs = text.split('\n\n')  # Split into paragraphs
            for paragraph in paragraphs:  # Process each paragraph individually, add a check to see if paragraph contained actual information.
                filecheck = list()
                filelist.append(file_path + ' ' + paragraph)
                filecheck.append({'role': 'system', 'content': f"You are an agent for an automated text-processing tool. You are one of many agents in a chain. Your task is to decide if the given text from a file was processed successfully. The processed text should contain factual data or opinions. If the given data only consists of an error message or a single question, skip it.  If the article was processed successfully, print: YES.  If a file-process is not needed, print: NO."})
                filecheck.append({'role': 'user', 'content': f"Is the processed information useful to an end-user? YES/NO: {paragraph}"})
                fileyescheck = chatgptyesno_completion(filecheck)
                if fileyescheck == 'YES':
                    print('---------')
                    print(file_path + ' ' + paragraph)
                    payload = list()
                    vector = gpt3_embedding(file_path + ' ' + paragraph)
                    timestamp = time()
                    timestring = timestamp_to_datetime(timestamp)
                    unique_id = str(uuid4())
                    metadata = {'bot': bot_name, 'time': timestamp, 'message': file_path + ' ' + paragraph,
                                'timestring': timestring, 'uuid': unique_id, "memory_type": "file_process"}
                    save_json(f'nexus/file_process_memory_nexus/%s.json' % unique_id, metadata)
                    payload.append((unique_id, vector, {"memory_type": "file_process"}))
                    vdb.upsert(payload, namespace=f'Tools_User_{username}_Bot_{bot_name}')
                    payload.clear()
                    filecheck.clear()
        table = filelist
        return table
    except Exception as e:
        print(e)
        table = "Error"
        return table  
                      
                      
def process_files_in_directory(directory_path, finished_directory_path, chunk_size=1000, overlap=100):
    try:
        files = os.listdir(directory_path)
        files = [f for f in files if os.path.isfile(os.path.join(directory_path, f))]
        with ThreadPoolExecutor() as executor:
            for file in files:
                executor.submit(process_and_move_file, directory_path, finished_directory_path, file, chunk_size, overlap)
    except Exception as e:
        print(e)
        table = "Error"
        return table  


def process_and_move_file(directory_path, finished_directory_path, file, chunk_size, overlap):
    try:
        file_path = os.path.join(directory_path, file)
        chunk_text_from_file(file_path, chunk_size, overlap)
        finished_file_path = os.path.join(finished_directory_path, file)
        shutil.move(file_path, finished_file_path)
    except Exception as e:
        print(e)
        table = "Error"
        return table  
        
# usage - process_files_in_directory('Text_Docs', 'Text_Docs/Finished')
        
        
def load_conversation_file_process_memory(results):
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    try:
        result = list()
        for m in results['matches']:
            info = load_json(f'nexus/file_process_memory_nexus/%s.json' % m['id'])
            result.append(info)
        ordered = sorted(result, key=lambda d: d['time'], reverse=False)  # sort them all chronologically
        messages = [i['message'] for i in ordered]
        return '\n'.join(messages).strip()
    except Exception as e:
        print(e)
        table = "Error"
        return table
        

def fail():
  #  print('')
    fail = "Not Needed"
    return fail
    
    
def search_file_process_db(line):
    m = multiprocessing.Manager()
    lock = m.Lock()
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    vdb = pinecone.Index("aetherius")
    try:
        with lock:
            line_vec = gpt3_embedding(line)
            results = vdb.query(vector=line_vec, filter={
        "memory_type": "file_process"}, top_k=30, namespace=f'Tools_User_{username}_Bot_{bot_name}')
            table = load_conversation_file_process_memory(results)
            return table
    except Exception as e:
        print(e)
        table = "Error"
        return table



def GPT_4_Text_Extract():
    vdb = pinecone.Index("aetherius")
    # # Number of Messages before conversation is summarized, higher number, higher api cost. Change to 3 when using GPT 3.5 due to token usage.
    conv_length = 4
    m = multiprocessing.Manager()
    lock = m.Lock()
    print("Type [Clear Memory] to clear saved short-term memory.")
    print("Type [Exit] to exit without saving.")
    tasklist = list()
    conversation = list()
    int_conversation = list()
    conversation2 = list()
    summary = list()
    auto = list()
    payload = list()
    consolidation  = list()
    tasklist_completion = list()
    master_tasklist = list()
    tasklist = list()
    tasklist_log = list()
    memcheck = list()
    memcheck2 = list()
    webcheck = list()
    counter = 0
    counter2 = 0
    mem_counter = 0
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    if not os.path.exists(f'nexus/{bot_name}/{username}/web_scrape_memory_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/web_scrape_memory_nexus')
    if not os.path.exists(f'nexus/{bot_name}/{username}/episodic_memory_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/episodic_memory_nexus')
    if not os.path.exists('Upload/TXT'):
        os.makedirs('Upload/TXT')
    if not os.path.exists('Upload/TXT/Finished'):
        os.makedirs('Upload/TXT/Finished')
    if not os.path.exists('Upload/PDF'):
        os.makedirs('Upload/PDF')
    if not os.path.exists('Upload/PDF/Finished'):
        os.makedirs('Upload/PDF/Finished')
    if not os.path.exists('Upload/EPUB'):
        os.makedirs('Upload/EPUB')
    if not os.path.exists('Upload/EPUB/Finished'):
        os.makedirs('Upload/EPUB/Finished')
    if not os.path.exists(f'nexus/file_process_memory_nexus'):
        os.makedirs(f'nexus/file_process_memory_nexus')
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
    main_prompt = open_file('./config/Chatbot_Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
    second_prompt = open_file('./config/Chatbot_Prompts/prompt_secondary.txt')
    greeting_msg = open_file('./config/Chatbot_Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
 #   r = sr.Recognizer()
    while True:
        # # Get Timestamp
        timestamp = time()
        timestring = timestamp_to_datetime(timestamp)
        process_files_in_directory('./Upload/SCANS', './Upload/SCANS/Finished')
        process_files_in_directory('./Upload/TXT', './Upload/TXT/Finished')
        process_files_in_directory('./Upload/PDF', './Upload/PDF/Finished')
        process_files_in_directory('./Upload/EPUB', './Upload/EPUB/Finished')
        # # Start or Continue Conversation based on if response exists
        conversation.append({'role': 'system', 'content': '%s' % main_prompt})
        int_conversation.append({'role': 'system', 'content': '%s' % main_prompt})
        if 'response_two' in locals():
            conversation.append({'role': 'user', 'content': a})
            if counter % conv_length == 0:
                print("\nConversation is continued, type [Exit] to clear conversation list.")
                conversation.append({'role': 'assistant', 'content': "%s" % response_two})
            pass
        else:
            conversation.append({'role': 'assistant', 'content': "%s" % greeting_msg})
            print("\n%s" % greeting_msg)
        print('---------')
        return
        
        
def OpenAi_Text_Extractor():
    set_dark_ancient_theme()
    root = tk.Tk()
    app = ChatBotApplication(root)
    app.master.geometry('650x500')  # Set the initial window size
    root.mainloop()