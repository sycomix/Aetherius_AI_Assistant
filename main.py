import os
import time
import sys
import importlib.util
sys.path.insert(0, './scripts')
import platform
import tkinter as tk
import customtkinter



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def set_dark_ancient_theme():
    background_color = "#2B303A"  # Dark blue-gray
    foreground_color = "#FDF7E3"  # Pale yellow
    button_color = "#415A77"  # Dark grayish blue
    highlight_color = "#FFB299"  # Peach
    text_color = 'white'

    return background_color, foreground_color, button_color, highlight_color


class SubApplication(tk.Toplevel):
    def __init__(self, parent, module, function_name):
        super().__init__(parent)
        self.title('Aetherius Sub Menu')
        self.geometry('720x500')  # adjust as needed
        customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
        self.parent = parent
        self.module = module
        self.function_name = function_name
        self.create_widgets()
        dark_bg_color = "#2b2b2b"  # Dark background color. You can adjust this value.
        self.configure(bg=dark_bg_color)  # Set the Toplevel's background color


    def create_widgets(self):
        font_config = open_file('./config/font.txt')
        font_size = open_file('./config/font_size.txt')

        self.label = customtkinter.CTkLabel(self, text="Select a script:", font=(font_config, 16, "bold"))
        self.label.pack(side="top", pady=10)

        files = os.listdir('scripts/' + self.function_name.replace('Menu_', ''))
        scripts = [file for file in files if file.endswith('.py')]
        for script in scripts:
            script_name = script[:-3].replace('_', ' ')
            button = customtkinter.CTkButton(self, text=script_name, command=lambda s=script: self.run_script(s), font=(font_config, 14))
            button.pack(side="top", pady=3)  # Added pady=5 for spacing between buttons

        exit_button = customtkinter.CTkButton(self, text="Exit", command=self.destroy)
        exit_button.pack(side="bottom")


    def run_script(self, script):
        module_name = script[:-3]
        spec = importlib.util.spec_from_file_location(module_name, f"scripts/{self.function_name.replace('Menu_', '')}/{script}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        function = getattr(module, module_name)
        function()


class Application(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title('Aetherius Main Menu')
        self.geometry('500x400')
        self.create_widgets()
        customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"

    def create_widgets(self):
        font_config = open_file('./config/font.txt')
        font_size = open_file('./config/font_size.txt')
        try:
            font_size_config = int(font_size)
        except:
            font_size_config = 10
        font_style = (f"{font_config}", font_size_config)
        font_style_bold = (f"{font_config}", font_size_config, "bold")




     #   self.configure(bg=background_color)
        self.label = customtkinter.CTkLabel(self, text="Welcome to the Aetherius Main Menu!", font=(font_config, 20, "bold"))
        self.label.pack(side="top", pady=10)

        self.label2 = customtkinter.CTkLabel(self, text="Please give a star on GitHub and\nshare with friends to support development!", font=(font_config, 14, "bold"))
        self.label2.pack(side="top", pady=10)

        self.label3 = customtkinter.CTkLabel(self, text="Select an Option:", font=("Arial", 14, "bold"))
        self.label3.pack(side="top", pady=10)

        files = os.listdir('scripts')
        scripts = [file for file in files if file.endswith('.py')]
        for script in scripts:
            script_name = script[:-3].replace('Menu_', '').replace('_', ' ')
            button = customtkinter.CTkButton(self, text=script_name, command=lambda s=script: self.run_script(s), font=("Arial", 14))
            button.pack(side="top", pady=3)

    def run_script(self, script):
        module_name = script[:-3]
        spec = importlib.util.spec_from_file_location(module_name, f"scripts/{script}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for attr_name in dir(module):
            if attr_name.startswith("Menu_"):
                SubApplication(self, module, attr_name)
                return

        tk.messagebox.showerror("Error", "No Menu_ function found")


if __name__ == '__main__':
  #  set_dark_ancient_theme()
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
    while True:
        app = Application()
        app.mainloop()
        continue