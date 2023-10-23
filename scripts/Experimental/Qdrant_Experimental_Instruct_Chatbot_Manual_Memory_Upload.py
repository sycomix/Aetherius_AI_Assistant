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
import importlib.util
from basic_functions import *
import multiprocessing
import threading
import concurrent.futures
import customtkinter
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, font, messagebox
# import speech_recognition as sr
# from gtts import gTTS
# from playsound import playsound
# import pyttsx3
# from pydub import AudioSegment
# from pydub.playback import play
# from pydub import effects
import requests
from sentence_transformers import SentenceTransformer
import shutil
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range
#from qdrant_client.http.models import Batch 
from qdrant_client.http import models
import numpy as np




def check_local_server_running():
    try:
        response = requests.get("http://localhost:6333/dashboard/")
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def open_file(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()

# Check if local server is running
if check_local_server_running():
    client = QdrantClient(url="http://localhost:6333")
    print("Connected to local Qdrant server.")
else:
    url = open_file('./api_keys/qdrant_url.txt')
    api_key = open_file('./api_keys/qdrant_api_key.txt')
    client = QdrantClient(url=url, api_key=api_key)
    print("Connected to cloud Qdrant server.")




# # # Comment out this and uncomment a choice below to run Aetherius Locally.

# client = QdrantClient(
# url=open_file('./api_keys/qdrant_url.txt'),
# api_key=open_file('./api_keys/qdrant_api_key.txt'),
# )



# Comment out Cloud Qdrant client code and uncomment this for local server
# client = QdrantClient(host="localhost", port=6333)


# # # Comments below are untested

# Comment out Cloud Qdrant client code and uncomment this for temporary bot that is deleted on shutdown.
# client = QdrantClient(":memory:")

# Comment out Cloud Qdrant client code and uncomment this for local disk
# client = QdrantClient(path="./nexus/qdrant")



# For local streaming, the websockets are hosted without ssl - http://
HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/chat'

# For reverse-proxied streaming, the remote will likely host with ssl - https://
# URI = 'https://your-uri-here.trycloudflare.com/api/v1/generate'


model = SentenceTransformer('all-mpnet-base-v2')

# encode = SentenceTransformer('all-mpnet-base-v2')


def oobabooga_terms(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 100,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"Your role is to interpret the original user query and generate 2-5 synonymous search terms in hyphenated bullet point structure that will guide the exploration of the chatbot's memory database. Each alternative term should reflect the essence of the user's initial search input. You are directly inputing your answer into the search query field. Only print the queries.",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.8,
        'top_p': 0.2,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
        return result['visible'][-1][1]


def oobabooga_inner_monologue(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 300,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"You are {bot_name}. Give a brief, first-person, silent soliloquy as your inner monologue that reflects on your contemplations in relation on how to respond to the user, {username}'s most recent message.  Directly print the inner monologue.",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.95,
        'top_p': 0.6,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.25,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
def oobabooga_intuition(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 450,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"Create a short predictive action plan in third person point of view as {bot_name} based on the user, {username}'s input. This response plan will be directly passed onto the main chatbot system to help plan the response to the user.  The character window is limited to 400 characters, leave out extraneous text to save space.  Please provide the truncated action plan in a tasklist format.  Focus on informational requests, do not get caught in loops of asking for more information.",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.7,
        'top_p': 0.15,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.20,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        

        
def oobabooga_episodicmem(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 300,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"Extract a single, short and concise third-person episodic memory based on {bot_name}'s final response for upload to a memory database.  You are directly inputing the memories into the database, only print the memory.",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.8,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
def oobabooga_flashmem(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 350,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"I will now combine the extracted data to form flashbulb memories in bullet point format, combining associated data. I will only include memories with a strong emotion attached, excluding redundant or irrelevant information.  You are directly inputing the memories into the database, only print the memories.",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.8,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
        
def oobabooga_implicitmem(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 350,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"Extract short and concise memories based on {bot_name}'s internal thoughts for upload to a memory database.  These should be executive summaries and will serve as the chatbots implicit memories.  You are directly inputing the memories into the database, only print the memories.  Print the response in the bullet point format: •IMPLICIT MEMORY: <Executive Summary>",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.8,
        'top_p': 0.6,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 30,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
def oobabooga_explicitmem(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 350,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"Extract a list of explicit memories based on {bot_name}'s final response for upload to a memory database.  These should be executive summaries and will serve as the chatbots explicit memories.  You are directly inputing the memories into the database, only print the memories.  Print the response in the bullet point format: •EXPLICIT MEMORY: <Executive Summary>",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.8,
        'top_p': 0.6,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 50,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
def oobabooga_consolidationmem(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 500,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"Read the Log and combine the different associated topics into executive summaries. Each summary should contain the entire context of the memory. Follow the format •Executive Summary",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.85,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 100,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
     #   print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
def oobabooga_associativemem(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 500,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"Read the Log and consolidate the different memories into executive summaries in a process allegorical to associative processing. Each summary should contain the entire context of the memory. Follow the bullet point format: •<EMOTIONAL TAG>: <CONSOLIDATED MEMORY>",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.7,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 100,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
     #   print(result['visible'][-1][1])
        return result['visible'][-1][1]


def oobabooga_250(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 250,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"{main_prompt}",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.8,
        'top_p': 0.2,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]



def oobabooga_500(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 500,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"{main_prompt}",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.85,
        'top_p': 0.2,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 100,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
     #   print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
def oobabooga_800(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 800,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"{main_prompt}",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.85,
        'top_p': 0.2,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 100,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
        
def oobabooga_response(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 1500,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"You are {bot_name}.  Read the conversation history, your inner monologue, action plan, and your memories.  Then, in first-person, generate a single comprehensive response to the user, {username}'s message.",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.87,
        'top_p': 0.6,
        'typical_p': 0.97,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.23,
        'repetition_penalty_range': 0,
        'top_k': 44,
        'min_length': 80,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
def oobabooga_auto(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 3,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"You are a sub-module of {bot_name}. Your purpose is to rate the given memory on a scale of 1-10. Only print a single number between one and ten.",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.6,
        'top_p': 0.3,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.25,
        'top_k': 30,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
        
def oobabooga_memyesno(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 10,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"You are a sub-agent for {bot_name}, an Autonomous Ai-Chatbot. Your purpose is to decide if the user's input requires {bot_name}'s past memories to complete. If the user's request pertains to information about the user, the chatbot, {bot_name}, or past personal events should be searched for in memory by printing 'YES'.  If memories are needed, print: 'YES'.  If they are not needed, print: 'NO'. You may only print YES or NO.",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.4,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 20,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
       
def oobabooga_selector(prompt):
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 10,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    #   'context_instruct': f"{main_prompt}",  # Optional
        'your_name': f'{username}',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.4,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 20,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        

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
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    if not os.path.exists(f'nexus/{bot_name}/{username}/cadence_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/cadence_nexus')
    while True:
        payload = []
    #    a = input(f'\n\nUSER: ')        
        timestamp = time()
        timestring = timestamp_to_datetime(timestamp)
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        # Create Qdrant client
    #    client = QdrantClient(":memory:")
    #    client = QdrantClient("./nexus/qdrant/{username}")
        # Define the collection name
        collection_name = f"Cadence_Bot_{bot_name}_User_{username}"
        # Create the collection only if it doesn't exist
        try:
            collection_info = client.get_collection(collection_name=collection_name)
        except:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
            )
        vector1 = model.encode([query])[0].tolist()
        unique_id = str(uuid4())
        point_id = unique_id + str(int(timestamp))
        metadata = {
            'bot': bot_name,
            'time': timestamp,
            'message': query,
            'timestring': timestring,
            'uuid': unique_id,
            'user': username,
            'memory_type': 'Cadence',
        }
        client.upsert(collection_name=collection_name,
                             points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])
    #        for hit in hits:
    #            print(hit.payload['message'])
    #        print('done')
    #    except Exception as e:
    #        print(f"Error:{str(e)}\nCollection not found errors will disapear when collection has an entry.")
        print('\n\nSYSTEM: Upload Successful!')
        return query
 
        
# Function for Uploading Heuristics, called in the create widgets function.
def DB_Upload_Heuristics(query):
    # key = input("Enter OpenAi API KEY:")
   # vdb = pinecone.Index("aetherius")
   # index_info = vdb.describe_index_stats()
   # print('Pinecone DB Info')
   # print(index_info)
   # print("Type [Delete All Data] to delete saved Heuristics.")
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    if not os.path.exists(f'nexus/{bot_name}/{username}/heuristics_nexus'):
        os.makedirs(f'nexus/{bot_name}/{username}/heuristics_nexus')
    while True:
        payload = []
    #    a = input(f'\n\nUSER: ')        
        timestamp = time()
        timestring = timestamp_to_datetime(timestamp)
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        # Define the collection name
        collection_name = f"Heuristics_Bot_{bot_name}_User_{username}"
        try:
            collection_info = client.get_collection(collection_name=collection_name)
        except:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
            )
        embedding = model.encode([query])[0].tolist()
        unique_id = str(uuid4())
        metadata = {
            'bot': bot_name,
            'time': timestamp,
            'message': query,
            'timestring': timestring,
            'uuid': unique_id,
            'memory_type': 'Heuristics',
        }
        client.upsert(collection_name=collection_name,
                             points=[PointStruct(id=unique_id, payload=metadata, vector=embedding)])  

    #    try:
    #        hits = client.search(
    #            collection_name=collection_name,
    #            query_vector=embedding,
    #            with_vectors=True,
    #            with_payload=True,
    #        )

        # Search the collection
        query_vector = embedding
        try:
            hits = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
            limit=5)

            # Print the result
            for hit in hits:
                print(hit)
            print('done')
        except Exception as e:
            print(f"Error:{str(e)}\nCollection not found errors will disapear when collection has an entry.")
        print('\n\nSYSTEM: Upload Successful!')
        return query
        
        
        
        
def upload_implicit_long_term_memories(query):
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    timestamp = time()
    timestring = timestamp_to_datetime(timestamp)
    payload = []
    payload = []
    collection_name = f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}"
    try:
        collection_info = client.get_collection(collection_name=collection_name)
    except:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
        )
    vector1 = model.encode([query])[0].tolist()
    unique_id = str(uuid4())
    point_id = unique_id + str(int(timestamp))
    metadata = {
        'bot': bot_name,
        'time': timestamp,
        'message': query,
        'timestring': timestring,
        'uuid': unique_id,
        'user': username,
        'memory_type': 'Implicit_Long_Term',
    }
    client.upsert(collection_name=collection_name,
                         points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])
    print('\n\nSYSTEM: Upload Successful!')
    return query
        
        
def upload_explicit_long_term_memories(query):
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    timestamp = time()
    timestring = timestamp_to_datetime(timestamp)
    payload = []
    payload = []
    collection_name = f"Explicit_Long_Term_Memory_Bot_{bot_name}_User_{username}"
    try:
        collection_info = client.get_collection(collection_name=collection_name)
    except:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
        )
    vector1 = model.encode([query])[0].tolist()
    unique_id = str(uuid4())
    point_id = unique_id + str(int(timestamp))
    metadata = {
        'bot': bot_name,
        'time': timestamp,
        'message': query,
        'timestring': timestring,
        'uuid': unique_id,
        'user': username,
        'memory_type': 'Explicit_Long_Term',
    }
    client.upsert(collection_name=collection_name,
                         points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])
    print('\n\nSYSTEM: Upload Successful!')
    return query
        
        
def ask_upload_implicit_memories(memories):
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    timestamp = time()
    timestring = timestamp_to_datetime(timestamp)
    payload = []
    if result := messagebox.askyesno(
        "Upload Memories", "Do you want to upload memories?"
    ):
        # User clicked "Yes"
        lines = memories.splitlines()
        for line in lines:
            if line.strip() == '':
                continue
            print(line)
            payload = []
            #    a = input(f'\n\nUSER: ')        
            # Define the collection name
            collection_name = f"Implicit_Short_Term_Memory_Bot_{bot_name}_User_{username}"
            # Create the collection only if it doesn't exist
            try:
                collection_info = client.get_collection(collection_name=collection_name)
            except:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                )
            vector1 = model.encode([line])[0].tolist()
            unique_id = str(uuid4())
            point_id = unique_id + str(int(timestamp))
            metadata = {
                'bot': bot_name,
                'time': timestamp,
                'message': line,
                'timestring': timestring,
                'uuid': unique_id,
                'user': username,
                'memory_type': 'Implicit_Short_Term',
            }
            client.upsert(collection_name=collection_name,
                                 points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])
        print('\n\nSYSTEM: Upload Successful!')
        return 'yes'
    else:
        # User clicked "No"
        print('\n\nSYSTEM: Memories have been Deleted.')
        
        
def ask_upload_explicit_memories(memories):
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    timestamp = time()
    timestring = timestamp_to_datetime(timestamp)
    payload = []
    if result := messagebox.askyesno(
        "Upload Memories", "Do you want to upload memories?"
    ):
        # User clicked "Yes"
        lines = memories.splitlines()
        for line in lines:
            if line.strip() == '':
                continue
            print(line)
            payload = []
            #    a = input(f'\n\nUSER: ')        
            # Define the collection name
            collection_name = f"Explicit_Short_Term_Memory_Bot_{bot_name}_User_{username}"
            # Create the collection only if it doesn't exist
            try:
                collection_info = client.get_collection(collection_name=collection_name)
            except:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                )
            vector1 = model.encode([line])[0].tolist()
            unique_id = str(uuid4())
            point_id = unique_id + str(int(timestamp))
            metadata = {
                'bot': bot_name,
                'time': timestamp,
                'message': line,
                'timestring': timestring,
                'uuid': unique_id,
                'user': username,
                'memory_type': 'Explicit_Short_Term',
            }
            client.upsert(collection_name=collection_name,
                                 points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])
        print('\n\nSYSTEM: Upload Successful!')
        return 'yes'
    else:
        # User clicked "No"
        print('\n\nSYSTEM: Memories have been Deleted.')
        
        
def ask_upload_episodic_memories(memories):
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    timestamp = time()
    timestring = timestamp_to_datetime(timestamp)
    if result := messagebox.askyesno(
        "Upload Memories", "Do you want to upload memories?"
    ):
        # User clicked "Yes"       
        # Create Qdrant client
    #    client = QdrantClient(":memory:")
    #    client = QdrantClient("./nexus/qdrant/{username}")
        # Define the collection name
        collection_name = f"Episodic_Memory_Bot_{bot_name}_User_{username}"
        # Create the collection only if it doesn't exist
        try:
            collection_info = client.get_collection(collection_name=collection_name)
        except:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
            )
        vector1 = model.encode([query])[0].tolist()
        unique_id = str(uuid4())
        point_id = unique_id + str(int(timestamp))
        metadata = {
            'bot': bot_name,
            'time': timestamp,
            'message': query,
            'timestring': timestring,
            'uuid': unique_id,
            'memory_type': 'Episodic',
        }
        payload = []
        client.upsert(collection_name=collection_name,
                             points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])
        return 'yes'
    else:
        # User clicked "No"
        print('\n\nSYSTEM: Memories have been Deleted.')
        
        
def ask_upload_memories(memories, memories2):
    username = open_file('./config/prompt_username.txt')
    bot_name = open_file('./config/prompt_bot_name.txt')
    timestamp = time()
    timestring = timestamp_to_datetime(timestamp)
    payload = []
    print(f'\nIMPLICIT MEMORIES\n-------------')
    print(memories)
    print(f'\nEXPLICIT MEMORIES\n-------------')
    print(memories2)
    if result := messagebox.askyesno(
        "Upload Memories", "Do you want to upload memories?"
    ):
        # User clicked "Yes"
        lines = memories.splitlines()
        for line in lines:
            if line.strip():
                continue
            print(line)
            payload = []
            #    a = input(f'\n\nUSER: ')        
            # Define the collection name
            collection_name = f"Implicit_Short_Term_Memory_Bot_{bot_name}_User_{username}"
            # Create the collection only if it doesn't exist
            try:
                collection_info = client.get_collection(collection_name=collection_name)
            except:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                )
            vector1 = model.encode([line])[0].tolist()
            unique_id = str(uuid4())
            point_id = unique_id + str(int(timestamp))
            metadata = {
                'bot': bot_name,
                'time': timestamp,
                'message': line,
                'timestring': timestring,
                'uuid': unique_id,
                'user': username,
                'memory_type': 'Implicit_Short_Term',
            }
            client.upsert(collection_name=collection_name,
                                 points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])
            # Search the collection
            payload.clear()
        lines = memories2.splitlines()
        for line in lines:
            if line.strip():
                continue
            print(line)
            payload = []
            #    a = input(f'\n\nUSER: ')        
            # Define the collection name
            collection_name = f"Explicit_Short_Term_Memory_Bot_{bot_name}_User_{username}"
            # Create the collection only if it doesn't exist
            try:
                collection_info = client.get_collection(collection_name=collection_name)
            except:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                )
            vector1 = model.encode([line])[0].tolist()
            unique_id = str(uuid4())
            point_id = unique_id + str(int(timestamp))
            metadata = {
                'bot': bot_name,
                'time': timestamp,
                'message': line,
                'timestring': timestring,
                'uuid': unique_id,
                'user': username,
                'memory_type': 'Explicit_Short_Term',
            }
            client.upsert(collection_name=collection_name,
                                 points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])
            payload.clear()
        print('\n\nSYSTEM: Upload Successful!')
        return 'yes'
    else:
        # User clicked "No"
        print('\n\nSYSTEM: Memories have been Deleted.')
        return 'no'
        
        
# Running Conversation List
class MainConversation:
    def __init__(self, max_entries, prompt, greeting):
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        self.max_entries = max_entries
        self.file_path = f'./history/{username}/{bot_name}_main_conversation_history.json'
        self.file_path2 = f'./history/{username}/{bot_name}_main_history.json'
        self.main_conversation = [prompt, greeting]

        # Load existing conversation from file
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.running_conversation = data.get('running_conversation', [])
        else:
            self.running_conversation = []

    def append(self, timestring, username, a, bot_name, response_two):
        # Append new entry to the running conversation
        entry = [f"{timestring}-{username}: {a}", f"Response: {response_two}"]
        self.running_conversation.append("\n\n".join(entry))  # Join the entry with "\n\n"

        # Remove oldest entry if conversation length exceeds max entries
        while len(self.running_conversation) > self.max_entries:
            self.running_conversation.pop(0)
        self.save_to_file()

    def save_to_file(self):
        # Combine main conversation and formatted running conversation for saving to file
        history = self.main_conversation + self.running_conversation

        data_to_save = {
            'main_conversation': self.main_conversation,
            'running_conversation': self.running_conversation
        }

        # save history as a list of dictionaries with 'visible' key
        data_to_save2 = {
            'history': [{'visible': entry} for entry in history]
        }

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)
        with open(self.file_path2, 'w', encoding='utf-8') as f:
            json.dump(data_to_save2, f, indent=4)

    def get_conversation_history(self):
        if not os.path.exists(self.file_path) or not os.path.exists(self.file_path2):
            self.save_to_file()
        return self.main_conversation + ["\n\n".join(entry.split("\n\n")) for entry in self.running_conversation]
        
    def get_last_entry(self):
        return self.running_conversation[-1] if self.running_conversation else None
        
    
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
            greeting_msg = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_greeting.txt').replace('<<NAME>>', bot_name)
            self.conversation_text.insert(tk.END, greeting_msg + '\n\n')
        self.conversation_text.yview(tk.END)
        
    
    # Edit Bot Name
    def choose_bot_name(self):
        username = open_file('./config/prompt_username.txt')
        if bot_name := simpledialog.askstring(
            "Choose Bot Name", "Type a Bot Name:"
        ):
            file_path = "./config/prompt_bot_name.txt"
            with open(file_path, 'w') as file:
                file.write(bot_name)
            base_path = "./config/Chatbot_Prompts"
            base_prompts_path = os.path.join(base_path, "Base")
            user_bot_path = os.path.join(base_path, username, bot_name)
            # Check if user_bot_path exists
            if not os.path.exists(user_bot_path):
                os.makedirs(user_bot_path)  # Create directory
                print(f'Created new directory at: {user_bot_path}')
                # Define list of base prompt files
                base_files = ['prompt_main.txt', 'prompt_greeting.txt', 'prompt_secondary.txt']
                # Copy the base prompts to the newly created folder
                for filename in base_files:
                    src = os.path.join(base_prompts_path, filename)
                    if os.path.isfile(src):  # Ensure it's a file before copying
                        dst = os.path.join(user_bot_path, filename)
                        shutil.copy2(src, dst)  # copy2 preserves file metadata
                        print(f'Copied {src} to {dst}')
                    else:
                        print(f'Source file not found: {src}')
            else:
                print(f'Directory already exists at: {user_bot_path}')
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()
            self.master.destroy()
            Qdrant_Experimental_Instruct_Chatbot_Manual_Memory_Upload()
        

    # Edit User Name
    def choose_username(self):
        bot_name = open_file('./config/prompt_bot_name.txt')
        if username := simpledialog.askstring(
            "Choose Username", "Type a Username:"
        ):
            file_path = "./config/prompt_username.txt"
            with open(file_path, 'w') as file:
                file.write(username)
            base_path = "./config/Chatbot_Prompts"
            base_prompts_path = os.path.join(base_path, "Base")
            user_bot_path = os.path.join(base_path, username, bot_name)
            # Check if user_bot_path exists
            if not os.path.exists(user_bot_path):
                os.makedirs(user_bot_path)  # Create directory
                print(f'Created new directory at: {user_bot_path}')
                # Define list of base prompt files
                base_files = ['prompt_main.txt', 'prompt_greeting.txt', 'prompt_secondary.txt']
                # Copy the base prompts to the newly created folder
                for filename in base_files:
                    src = os.path.join(base_prompts_path, filename)
                    if os.path.isfile(src):  # Ensure it's a file before copying
                        dst = os.path.join(user_bot_path, filename)
                        shutil.copy2(src, dst)  # copy2 preserves file metadata
                        print(f'Copied {src} to {dst}')
                    else:
                        print(f'Source file not found: {src}')
            else:
                print(f'Directory already exists at: {user_bot_path}')
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()
            self.master.destroy()
            Qdrant_Experimental_Instruct_Chatbot_Manual_Memory_Upload()
        
        
    # Edits Main Chatbot System Prompt
    def Edit_Main_Prompt(self):
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        file_path = f"./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt"

        with open(file_path, 'r', encoding='utf-8') as file:
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
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        file_path = f"./config/Chatbot_Prompts/{username}/{bot_name}/prompt_secondary.txt"
        
        with open(file_path, 'r', encoding='utf-8') as file:
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

        with open(file_path, 'r', encoding='utf-8') as file:
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

        with open(file_path, 'r', encoding='utf-8') as file:
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
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        file_path = f"./config/Chatbot_Prompts/{username}/{bot_name}/prompt_greeting.txt"
        
        with open(file_path, 'r', encoding='utf-8') as file:
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

        with open(file_path, 'r', encoding='utf-8') as file:
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
        
        button_frame = tk.Frame(top)
        button_frame.pack()

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
                entry_lines = entry_text.get("1.0", tk.END).strip()
                running_conversation[entry_index + i] = entry_lines

            conversation_data["running_conversation"] = running_conversation

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(conversation_data, file, indent=4, ensure_ascii=False)

            # Update your conversation display or perform any required actions here
            self.conversation_text.delete("1.0", tk.END)
            self.display_conversation_history()
            update_entry()  # Update the displayed entry in the cycling menu

            # Update the entry number label after saving the changes
            entry_number_label.config(text=f"Entry {entry_index + 1}/{len(running_conversation)}")
        
        def delete_entry():
            nonlocal entry_index
            if len(running_conversation) == 1:
                # If this is the last entry, simply clear the entry_text
                entry_text.delete("1.0", tk.END)
                running_conversation.clear()
            else:
                # Delete the current entry from the running conversation list
                del running_conversation[entry_index]

                # Adjust the entry_index if it exceeds the valid range
                if entry_index >= len(running_conversation):
                    entry_index = len(running_conversation) - 1

                # Update the displayed entry
                update_entry()
                entry_number_label.config(text=f"Entry {entry_index + 1}/{len(running_conversation)}")

            # Save the conversation after deleting an entry
            save_conversation()

        save_button = tk.Button(button_frame, text="Save", command=save_conversation)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)

        delete_button = tk.Button(button_frame, text="Delete", command=delete_entry)
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Configure the top level window to scale with the content
        top.pack_propagate(False)
        top.geometry("600x400")  # Set the initial size of the window
        
        
    # Selects which Open Ai model to use.    
    def Model_Selection(self):
        file_path = "./config/model.txt"
        
        with open(file_path, 'r', encoding='utf-8') as file:
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
        query_label.grid(row=0, column=0, padx=5, pady=5)

        query_entry = tk.Entry(cadence_window)
        query_entry.grid(row=1, column=0, padx=5, pady=5)

        results_label = tk.Label(cadence_window, text="Scrape results: ")
        results_label.grid(row=2, column=0, padx=5, pady=5)

        results_text = tk.Text(cadence_window)
        results_text.grid(row=3, column=0, padx=5, pady=5)

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

        def delete_cadence():
            # Replace 'username' and 'bot_name' with appropriate variables if available.
            # You may need to adjust 'vdb' based on how your database is initialized.
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete heuristics?")
            if confirm:
                client.delete_collection(collection_name=f"Cadence_Bot_{bot_name}_User_{username}")
                # Clear the results_text widget after deleting heuristics (optional)
                results_text.delete("1.0", tk.END)  

        search_button = tk.Button(cadence_window, text="Upload", command=perform_search)
        search_button.grid(row=4, column=0, padx=5, pady=5)

        # Use `side=tk.LEFT` for the delete button to position it at the top-left corner
        delete_button = tk.Button(cadence_window, text="Delete Cadence", command=delete_cadence)
        delete_button.grid(row=5, column=0, padx=5, pady=5)
        
        
        
        
    def open_heuristics_window(self):
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        heuristics_window = tk.Toplevel(self)
        heuristics_window.title("Heuristics DB Upload")


        query_label = tk.Label(heuristics_window, text="Enter Heuristics:")
        query_label.grid(row=0, column=0, padx=5, pady=5)

        query_entry = tk.Entry(heuristics_window)
        query_entry.grid(row=1, column=0, padx=5, pady=5)

        results_label = tk.Label(heuristics_window, text="Entered Heuristics: ")
        results_label.grid(row=2, column=0, padx=5, pady=5)

        results_text = tk.Text(heuristics_window)
        results_text.grid(row=3, column=0, padx=5, pady=5)

        def perform_search():
            query = query_entry.get()

            def update_results(query):
                # Update the GUI with the new paragraph
                results_text.insert(tk.END, f"{query}\n\n")
                results_text.yview(tk.END)
                query_entry.delete(0, tk.END)

            def search_task():
                # Call the modified GPT_3_5_Tasklist_Web_Search function with the callback
                search_results = DB_Upload_Heuristics(query)

                # Use the `after` method to schedule the `update_results` function on the main Tkinter thread
                heuristics_window.after(0, update_results, search_results)
                   
            t = threading.Thread(target=search_task)
            t.start()
                
        def delete_heuristics():
            # Replace 'username' and 'bot_name' with appropriate variables if available.
            # You may need to adjust 'vdb' based on how your database is initialized.
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete heuristics?")
            if confirm:
                client.delete_collection(collection_name=f"Heuristics_Bot_{bot_name}_User_{username}")
                # Clear the results_text widget after deleting heuristics (optional)
                results_text.delete("1.0", tk.END)  

        search_button = tk.Button(heuristics_window, text="Upload", command=perform_search)
        search_button.grid(row=4, column=0, padx=5, pady=5)

        # Use `side=tk.LEFT` for the delete button to position it at the top-left corner
        delete_button = tk.Button(heuristics_window, text="Delete Heuristics", command=delete_heuristics)
        delete_button.grid(row=5, column=0, padx=5, pady=5)
        
        
    def open_long_term_window(self):
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        long_term_window = tk.Toplevel(self)
        long_term_window.title("Long Term Memory DB Upload")


        query_label = tk.Label(long_term_window, text="Enter Memory:")
        query_label.grid(row=0, column=0, padx=5, pady=5)

        query_entry = tk.Entry(long_term_window)
        query_entry.grid(row=1, column=0, padx=5, pady=5)

        results_label = tk.Label(long_term_window, text="Entered Memories: ")
        results_label.grid(row=2, column=0, padx=5, pady=5)

        results_text = tk.Text(long_term_window)
        results_text.grid(row=3, column=0, padx=5, pady=5)

        def perform_implicit_upload():
            query = query_entry.get()

            def update_results(query):
                # Update the GUI with the new paragraph
                results_text.insert(tk.END, f"{query}\n\n")
                results_text.yview(tk.END)
                query_entry.delete(0, tk.END)

            def search_task():
                # Call the modified GPT_3_5_Tasklist_Web_Search function with the callback
                search_results = upload_implicit_long_term_memories(query)

                # Use the `after` method to schedule the `update_results` function on the main Tkinter thread
                long_term_window.after(0, update_results, search_results)
                   
            t = threading.Thread(target=search_task)
            t.start()
            
            
        def perform_explicit_upload():
            query = query_entry.get()

            def update_results(query):
                # Update the GUI with the new paragraph
                results_text.insert(tk.END, f"{query}\n\n")
                results_text.yview(tk.END)
                query_entry.delete(0, tk.END)

            def search_task():
                # Call the modified GPT_3_5_Tasklist_Web_Search function with the callback
                search_results = upload_explicit_long_term_memories(query)

                # Use the `after` method to schedule the `update_results` function on the main Tkinter thread
                long_term_window.after(0, update_results, search_results)
                   
            t = threading.Thread(target=search_task)
            t.start()


        implicit_search_button = tk.Button(long_term_window, text="Implicit Upload", command=perform_implicit_upload)
        implicit_search_button.grid(row=4, column=0, padx=5, pady=5, columnspan=1)  # Set columnspan to 1

        explicit_search_button = tk.Button(long_term_window, text="Explicit Upload", command=perform_explicit_upload)
        explicit_search_button.grid(row=5, column=0, padx=5, pady=5, columnspan=1) 
        

        
        
    def open_deletion_window(self):
    #    vdb = pinecone.Index("aetherius")
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        deletion_window = tk.Toplevel(self)
        deletion_window.title("DB Deletion Menu")
        
        
        def delete_cadence():
                # Replace 'username' and 'bot_name' with appropriate variables if available.
                # You may need to adjust 'vdb' based on how your database is initialized.
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete saved cadence?")
            if confirm:
                client.delete_collection(collection_name=f"Cadence_Bot_{bot_name}_User_{username}")
        
    
        def delete_heuristics():
                # Replace 'username' and 'bot_name' with appropriate variables if available.
                # You may need to adjust 'vdb' based on how your database is initialized.
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete heuristics?")
            if confirm:
                client.delete_collection(collection_name=f"Heuristics_Bot_{bot_name}_User_{username}")
                
                
        def delete_counters():
                # Replace 'username' and 'bot_name' with appropriate variables if available.
                # You may need to adjust 'vdb' based on how your database is initialized.
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete memory consolidation counters?")
            if confirm:
                client.delete_collection(collection_name=f"Flash_Counter_Bot_{bot_name}_User_{username}")
                client.delete_collection(collection_name=f"Consol_Counter_Bot_{bot_name}_User_{username}")
                
                
        def delete_bot():
                # Replace 'username' and 'bot_name' with appropriate variables if available.
                # You may need to adjust 'vdb' based on how your database is initialized.
            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to delete {bot_name} in their entirety?")
            if confirm:
                client.delete_collection(collection_name=f"Implicit_Short_Term_Memory_Bot_{bot_name}_User_{username}")
                client.delete_collection(collection_name=f"Explicit_Short_Term_Memory_Bot_{bot_name}_User_{username}")
                client.delete_collection(collection_name=f"Episodic_Memory_Bot_{bot_name}_User_{username}")
                client.delete_collection(collection_name=f"Explicit_Long_Term_Memory_Bot_{bot_name}_User_{username}")
                client.delete_collection(collection_name=f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}")
                client.delete_collection(collection_name=f"Heuristics_Bot_{bot_name}_User_{username}")
                client.delete_collection(collection_name=f"Cadence_Bot_{bot_name}_User_{username}")
                client.delete_collection(collection_name=f"Flash_Counter_Bot_{bot_name}_User_{username}")
                client.delete_collection(collection_name=f"Consol_Counter_Bot_{bot_name}_User_{username}")
                client.delete_collection(collection_name=f"Flashbulb_Memory_Bot_{bot_name}_User_{username}")
                
                
        delete_cadence_button = tk.Button(deletion_window, text="Delete Cadence", command=delete_cadence)
        delete_cadence_button.pack()
                
        delete_heuristics_button = tk.Button(deletion_window, text="Delete Heuristics", command=delete_heuristics)
        delete_heuristics_button.pack()
        
        delete_counters_button = tk.Button(deletion_window, text="Delete Memory Consolidation Counters", command=delete_counters)
        delete_counters_button.pack()
        
        delete_bot_button = tk.Button(deletion_window, text="Delete Entire Chatbot", command=delete_bot)
        delete_bot_button.pack()
        
        
        
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
        if selection == "Cadence DB":
            self.open_cadence_window()
        elif selection == "Heuristics DB":
            self.open_heuristics_window()
        elif selection == "Long Term Memory DB":
            self.open_long_term_window()
        elif selection == "DB Deletion":
            self.open_deletion_window()    

        
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
        self.db_menu = ttk.Combobox(self.top_frame, values=["DB Management", "----------------------------", "Cadence DB", "Heuristics DB", "Long Term Memory DB", "DB Deletion"], state="readonly")
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
            Qdrant_Experimental_Instruct_Chatbot_Manual_Memory_Upload()
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
        # # Number of Messages before conversation is summarized, higher number, higher api cost. Change to 3 when using GPT 3.5 due to token usage.
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
        counter = 0
        counter2 = 0
        mem_counter = 0
        length_config = open_file('./config/Conversation_Length.txt')
        conv_length = 3
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        botnameupper = bot_name.upper()
        usernameupper = username.upper()
    #    base_path = "./config/Chatbot_Prompts"
    #    base_prompts_path = os.path.join(base_path, "Base")
    #    user_bot_path = os.path.join(base_path, username, bot_name)
    #    if not os.path.exists(user_bot_path):
    #        os.makedirs(user_bot_path)  # Create directory
    #        print(f'Created new directory at: {user_bot_path}')
    #    # Copy the base prompts to the newly created folder
    #        for filename in os.listdir(base_prompts_path):
    #            src = os.path.join(base_prompts_path, filename)
    ##            dst = os.path.join(user_bot_path, filename)
     #           shutil.copy2(src, dst)
        base_path = "./config/Chatbot_Prompts"
        base_prompts_path = os.path.join(base_path, "Base")
        user_bot_path = os.path.join(base_path, username, bot_name)

        # Check if user_bot_path exists
        if not os.path.exists(user_bot_path):
            os.makedirs(user_bot_path)  # Create directory
            print(f'Created new directory at: {user_bot_path}')

            # Define list of base prompt files
            base_files = ['prompt_main.txt', 'prompt_greeting.txt', 'prompt_secondary.txt']

            # Copy the base prompts to the newly created folder
            for filename in base_files:
                src = os.path.join(base_prompts_path, filename)
                if os.path.isfile(src):  # Ensure it's a file before copying
                    dst = os.path.join(user_bot_path, filename)
                    shutil.copy2(src, dst)  # copy2 preserves file metadata
                    print(f'Copied {src} to {dst}')
                else:
                    print(f'Source file not found: {src}')
        else:
            print(f'Directory already exists at: {user_bot_path}')
        main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_secondary.txt')
        greeting_msg = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_greeting.txt').replace('<<NAME>>', bot_name)
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
        #   r = sr.Recognizer()
        while True:
            conversation_history = main_conversation.get_last_entry()
            # # Get Timestamp
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            
            history = {'internal': [], 'visible': []}

            con_hist = f'{conversation_history}'
            # # Start or Continue Conversation based on if response exists
        #    conversation.append({'role': 'system', 'content': f"%MAIN CHATBOT SYSTEM PROMPT%\n{main_prompt}\n\n"})
        #    int_conversation.append({'role': 'system', 'content': f"MAIN CHATBOT SYSTEM PROMPT: {main_prompt}\n\n"})
        #    int_conversation.append({'role': 'system', 'content': f"CONVERSATION HISTORY: {con_hist}[/INST]\n\n"})
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
            vector_input = model.encode([message_input])[0].tolist()
            conversation.append({'role': 'user', 'content': f"USER INPUT: {a}\n\n\n"})        
            # # Generate Semantic Search Terms
            tasklist.append({'role': 'system', 'content': "SYSTEM: You are a semantic rephraser. Your role is to interpret the original user query and generate 2-5 synonymous search terms that will guide the exploration of the chatbot's memory database. Each alternative term should reflect the essence of the user's initial search input. Please list your results using a hyphenated bullet point structure.\n\n"})
            tasklist.append({'role': 'user', 'content': "USER: %s\n\nASSISTANT: Sure, I'd be happy to help! Here are 2-5 synonymous search terms:\n" % a})
        #    tasklist.append({'role': 'assistant', 'content': "[/INST]"})
            prompt = ''.join([message_dict['content'] for message_dict in tasklist])
            tasklist_output = oobabooga_terms(prompt)
            print(tasklist_output)
            print('\n-----------------------\n')
            lines = tasklist_output.splitlines()
            db_term = {}
            db_term_result = {}
            db_term_result2 = {}
            tasklist_counter = 0
            tasklist_counter2 = 0
            vector_input1 = model.encode([message_input])[0].tolist()
            for line in lines:            
                try:
                    hits = client.search(
                        collection_name=f"Explicit_Long_Term_Memory_Bot_{bot_name}_User_{username}",
                        query_vector=vector_input1,
                    limit=4)
                    # Print the result
                #    for hit in hits:
                #        print(hit.payload['message'])
                    db_search_16 = [hit.payload['message'] for hit in hits]
                    conversation.append({'role': 'assistant', 'content': f"LONG TERM CHATBOT MEMORIES: {db_search_16}\n"})
                    tasklist_counter + 1
                    if tasklist_counter < 4:
                        int_conversation.append({'role': 'assistant', 'content': f"{botnameupper}'S LONG TERM MEMORIES: {db_search_16}\n"})
                    print(db_search_16)
                    print('done')
                except Exception as e:
                    print(f"An unexpected error occurred: {str(e)}")
                try:
                    hits = client.search(
                        collection_name=f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}",
                        query_vector=vector_input1,
                    limit=4)
                    # Print the result
                #    for hit in hits:
                #        print(hit.payload['message'])
                    db_search_17 = [hit.payload['message'] for hit in hits]
                    conversation.append({'role': 'assistant', 'content': f"LONG TERM CHATBOT MEMORIES: {db_search_17}\n"})
                    tasklist_counter2 + 1
                    if tasklist_counter2 < 4:
                        int_conversation.append({'role': 'assistant', 'content': f"{botnameupper}'S LONG TERM MEMORIES: {db_search_17}\n"})
                    print(db_search_17)
                    print('done')
                except Exception as e:
                    print(f"An unexpected error occurred: {str(e)}")

            print('\n-----------------------\n')
            db_search_1, db_search_2, db_search_3, db_search_14 = None, None, None, None
            try:
                hits = client.search(
                    collection_name=f"Episodic_Memory_Bot_{bot_name}_User_{username}",
                    query_vector=vector_input1,
                limit=6)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])
                db_search_1 = [hit.payload['message'] for hit in hits]
                print(db_search_1)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            try:
                hits = client.search(
                    collection_name=f"Explicit_Short_Term_Memory_Bot_{bot_name}_User_{username}",
                    query_vector=vector_input1,
                limit=5)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])
                db_search_2 = [hit.payload['message'] for hit in hits]
                print(db_search_2)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            try:
                hits = client.search(
                    collection_name=f"Flashbulb_Memory_Bot_{bot_name}_User_{username}",
                    query_vector=vector_input1,
                limit=2)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])  
                db_search_3 = [hit.payload['message'] for hit in hits]
                print(db_search_3)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            try:
                hits = client.search(
                    collection_name=f"Heuristics_Bot_{bot_name}_User_{username}",
                    query_vector=vector_input1,
                limit=5)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])
                db_search_14 = [hit.payload['message'] for hit in hits]
                print(db_search_14)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            # # Inner Monologue Generation
         #   conversation.append({'role': 'system', 'content': f"CONVERSATION HISTORY: {con_hist}[/INST]\n\n"})
            conversation.append({'role': 'assistant', 'content': f"{botnameupper}'S EPISODIC MEMORIES: {db_search_1}\n{db_search_3}\n\n{botnameupper}'S SHORT-TERM MEMORIES: {db_search_2}.\n\n{botnameupper}'s HEURISTICS: {db_search_14}\n\n\n\nSYSTEM:Compose a short silent soliloquy to serve as {bot_name}'s internal monologue/narrative.  Ensure it includes {bot_name}'s contemplations and emotions in relation to {username}'s request.\n\n\nCURRENT CONVERSATION HISTORY: {con_hist}\n\n\n{usernameupper}/USER MESSAGE: {a}\nPlease directly provide a short internal monologue as {bot_name} contemplating the user's most recent message.\n\nASSISTANT:{botnameupper}: Of course, here is an inner soliloquy for {bot_name}:"})
            prompt = ''.join([message_dict['content'] for message_dict in conversation])
            output_one = oobabooga_inner_monologue(prompt)
            inner_output = (f'{output_one}\n\n')
            paragraph = output_one
            vector_monologue = model.encode([paragraph])[0].tolist()
            print('\n\nINNER_MONOLOGUE: %s' % output_one)
            print('\n-----------------------\n')
            # # Clear Conversation List
            conversation.clear()
            # Update the GUI elements on the main thread
            self.master.after(0, self.update_inner_monologue, inner_output)
            # After the operations are complete, call the GPT_Intuition function in a separate thread
            t = threading.Thread(target=self.GPT_Intuition, args=(a, vector_input, output_one, int_conversation))
            t.start()
            return
            
            
    def update_inner_monologue(self, output_one):
        self.conversation_text.insert(tk.END, f"Inner Monologue: {output_one}\n\n")
        self.conversation_text.yview(tk.END)

            
    def GPT_Intuition(self, a, vector_input, output_one, int_conversation):
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
        conv_length = 3
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        botnameupper = bot_name.upper()
        usernameupper = username.upper()
        main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_secondary.txt')
        greeting_msg = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_greeting.txt').replace('<<NAME>>', bot_name)
        main_conversation = MainConversation(conv_length, main_prompt, greeting_msg)
    #   r = sr.Recognizer()
        while True:
            conversation_history = main_conversation.get_conversation_history()
            # # Get Timestamp
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            con_hist = f'{conversation_history}'
            # # Start or Continue Conversation based on if response exists
            conversation.append({'role': 'system', 'content': f"CHATBOT GREETING: {greeting_msg}\n\n"})
    #        int_conversation.append({'role': 'system', 'content': f"%MAIN SYSTEM PROMPT%\n{con_hist}\n\n"})
    #        if 'response_two' in locals():
    #            int_conversation.append({'role': 'assistant', 'content': f"%GREETING%\n{greeting_msg}\n\n"})
    #            int_conversation.append({'role': 'assistant', 'content': f"%PREVIOUS CHATBOT RESPONSE%\n{response_two}\n\n"})
    #            pass
    #        else:
    #            int_conversation.append({'role': 'assistant', 'content': f"%GREETING%\n{greeting_msg}\n\n"})
           #     print("\n%s" % greeting_msg)
            message = output_one
        #    vector_monologue = model.encode([message]).tolist()
            # # Memory DB Search     
            vector_monologue = model.encode([message])[0].tolist()
            db_search_4, db_search_5, db_search_12, db_search_15 = None, None, None, None
            try:
                hits = client.search(
                    collection_name=f"Episodic_Memory_Bot_{bot_name}_User_{username}",
                    query_vector=vector_monologue,
                limit=3)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])
                db_search_4 = [hit.payload['message'] for hit in hits]
                print(db_search_4)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            try:
                hits = client.search(
                    collection_name=f"Explicit_Short_Term_Memory_Bot_{bot_name}_User_{username}",
                    query_vector=vector_monologue,
                limit=3)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])
                db_search_5 = [hit.payload['message'] for hit in hits]
                print(db_search_5)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            try:
                hits = client.search(
                    collection_name=f"Flashbulb_Memory_Bot_{bot_name}_User_{username}",
                    query_vector=vector_monologue,
                limit=2)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])  
                db_search_12 = [hit.payload['message'] for hit in hits]
                print(db_search_12)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            try:
                hits = client.search(
                    collection_name=f"Heuristics_Bot_{bot_name}_User_{username}",
                    query_vector=vector_monologue,
                limit=5)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])
                db_search_15 = [hit.payload['message'] for hit in hits]
                print(db_search_15)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            print('\n-----------------------\n')
            # # Intuition Generation
        #    int_conversation.append({'role': 'user', 'content': f"USER INPUT: {a}\n\n"})
            int_conversation.append({'role': 'assistant', 'content': f"{botnameupper}'S FLASHBULB MEMORIES: {db_search_12}\n{botnameupper}'S EXPLICIT MEMORIES: {db_search_5}\n{botnameupper}'s HEURISTICS: {db_search_15}\n{botnameupper}'S INNER THOUGHTS: {output_one}\n{botnameupper}'S EPISODIC MEMORIES: {db_search_4}\nPREVIOUS CONVERSATION HISTORY: {con_hist}\n\n\n\nSYSTEM: Transmute the user, {username}'s message as {bot_name} by devising a truncated predictive action plan in the third person point of view on how to best respond to {username}'s most recent message. You are not allowed to use external resources.  Do not create a plan for generic conversation.  If the user is requesting information on a subject, give a plan on what information needs to be provided.\n\n\n{usernameupper}: {a}\nPlease only provide the third person action plan in your response.  The action plan should be in tasklist form.\n\nASSISTANT:{botnameupper}: Sure, here is a tasklist detailing how I should respond to the user:"}) 
            prompt = ''.join([message_dict['content'] for message_dict in int_conversation])
            output_two = oobabooga_intuition(prompt)
        #    message = output_one
         #   output_two = chatgpt200_completion(int_conversation)
            message_two = output_two
            print('\n\nINTUITION: %s' % output_two)
            print('\n-----------------------\n')
            # # Generate Implicit Short-Term Memory
            conversation.append({'role': 'user', 'content': f"USER INPUT: {a}\n\n"})
            implicit_short_term_memory = f'\nUSER: {a}\nINNER_MONOLOGUE: {output_one}'
            conversation.append({'role': 'assistant', 'content': f"LOG: {implicit_short_term_memory}\n\nINSTRUCTIONS: Read the log, extract the salient points about {bot_name} and {username}, then create short executive summaries listed in bullet points to serve as {bot_name}'s implicit memories. Each bullet point should be considered a separate memory and contain all context. Combining associated topics. Ignore the greeting prompt, it only exists for initial context. Use the hyphenated bullet point format: <-IMPLICIT MEMORY>\n<-IMPLICIT MEMORY>"})
        #    inner_loop_response = chatgpt200_completion(conversation)

        #    summary.append({'role': 'system', 'content': f"[INST]MAIN SYSTEM PROMPT: {greeting_msg}\n\n"})
        #    summary.append({'role': 'user', 'content': f"USER INPUT: {a}\n\n"})
            db_msg = f"\nUSER: {a}\nINNER_MONOLOGUE: {output_one}"
            summary.append({'role': 'assistant', 'content': f"LOG: {implicit_short_term_memory}\n\nSYSTEM: Read the log, extract the salient points about {bot_name} and {username} mentioned in the chatbot's inner monologue, then create a list of short executive summaries in bullet point format to serve as {bot_name}'s implicit memories. Each bullet point should be considered a separate memory and contain full context.  Use the bullet point format: •IMPLICIT MEMORY: <Executive Summary>\n\nASSISTANT:{botnameupper}: Sure! Here are the implicit memories based on {bot_name}'s internal thoughts:"})
            
            
            
            prompt = ''.join([message_dict['content'] for message_dict in summary])
            inner_loop_response = oobabooga_implicitmem(prompt)
            print(inner_loop_response)
            summary.clear()
        #    print(inner_loop_response)
        #    print('\n-----------------------\n')
            inner_loop_db = inner_loop_response
            paragraph = inner_loop_db
            vector = model.encode([paragraph])[0].tolist()
        #    vector = gpt3_embedding(inner_loop_db)
            conversation.clear()
            # # Auto Implicit Short-Term Memory DB Upload Confirmation
    #        auto_count = 0
    #        auto.clear()
        #    auto.append({'role': 'system', 'content': f'MAIN CHATBOT SYSTEM PROMPT: {main_prompt}\n\n'})
        #    auto.append({'role': 'user', 'content': "CURRENT SYSTEM PROMPT: You are a sub-module designed to reflect on your thought process. You are only able to respond with integers on a scale of 1-10, being incapable of printing letters.\n\n\n\n"})
        #    auto.append({'role': 'user', 'content': f"[INST]USER INPUT: {a}\n"})
    #        auto.append({'role': 'assistant', 'content': f"USER INPUT: {a}\n\nCHATBOTS INNER THOUGHTS: {output_one}\n\n\nINSTRUCTIONS: Please rate the chatbot's inner thoughts on a scale of 1 to 10. The rating will be directly input into a field, so ensure you only print a single number between 1 and 10.\n\nSUB-MODULE:"})
    #        auto_int = None
    #        while auto_int is None:
    #            prompt = ''.join([message_dict['content'] for message_dict in auto])
    #            automemory = oobabooga_auto(prompt)
    #        #    automemory = chatgptyesno_completion(auto)
    #            print(automemory)
    #            values_to_check = ["7", "8", "9", "10"]
    #            if any(val in automemory for val in values_to_check):
    #                auto_int = ('Pass')
    #                lines = inner_loop_db.splitlines()
    #                for line in lines:
    #                    if line.strip() == '':  # This condition checks for blank lines
    #                        continue
    #                    else:
    #                        print(line)
    #                        payload = list()
    #                    #    a = input(f'\n\nUSER: ')        
    #                        # Define the collection name
    #                        collection_name = f"Implicit_Short_Term_Memory_Bot_{bot_name}_User_{username}"
    #                        # Create the collection only if it doesn't exist
    #                        try:
    #                            collection_info = client.get_collection(collection_name=collection_name)
    #                        except:
    #                            client.create_collection(
    #                                collection_name=collection_name,
    #                                vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
    #                            )
    #                        vector1 = model.encode([line])[0].tolist()
    #                        unique_id = str(uuid4())
    #                        point_id = unique_id + str(int(timestamp))
    #                        metadata = {
    #                            'bot': bot_name,
    #                            'time': timestamp,
    #                            'message': line,
    #                            'timestring': timestring,
    #                            'uuid': unique_id,
    #                            'user': username,
    #                            'memory_type': 'Implicit_Short_Term',
    #                        }
    #                        client.upsert(collection_name=collection_name,
    #                                             points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])  
    #                        payload.clear()
    #                else:
    #                    print('-----------------------')
    #                    break
    #                print('\n-----------------------\n')        
    #                print('SYSTEM: Auto-memory upload Successful!')
    #                print('\n-----------------------\n')
    #            else:
    #                print("automemory failed to produce a rating. Retrying...")
    #                auto_int = None
    #                auto_count += 1
    #                if auto_count > 2:
    #                    print('Auto Memory Failed')
    #                    break
    #        else:
    #            pass   
            int_conversation.clear()
        #    self.master.after(0, self.update_intuition, output_two)
        #    print(f"Upload Memories?\n{inner_loop_response}\n\n")
        #    self.conversation_text.insert(tk.END, f"Upload Memories?\n{inner_loop_response}\n\n")
        #    ask_upload_implicit_memories(inner_loop_response)
            # After the operations are complete, call the response generation function in a separate thread
            t = threading.Thread(target=self.GPT_Response, args=(a, output_one, output_two, inner_loop_response))
            t.start()
            return   
                
                
    def update_intuition(self, output_two):
        self.conversation_text.insert(tk.END, f"Intuition: {output_two}\n\n")
        self.conversation_text.yview(tk.END)
                
                
    def GPT_Response(self, a, output_one, output_two, inner_loop_response):
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
        conv_length = 3
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        botnameupper = bot_name.upper()
        usernameupper = username.upper()
        main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_secondary.txt')
        greeting_msg = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_greeting.txt').replace('<<NAME>>', bot_name)
        main_conversation = MainConversation(conv_length, main_prompt, greeting_msg)
    #   r = sr.Recognizer()
        while True:
            conversation_history = main_conversation.get_conversation_history()
            # # Get Timestamp
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
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
            vector_input = model.encode([message_input])[0].tolist()
            # # Check for Commands
            # # Check for "Clear Memory"
            message = output_one
            vector_monologue = model.encode([message])[0].tolist()
        # # Update Second Conversation List for Response
            print('\n-----------------------\n')
            print('\n%s is thinking...\n' % bot_name)
            con_hist = f'{conversation_history}'
            conversation2.append({'role': 'system', 'content': f"PERSONALITY PROMPT: {main_prompt}\n\n"})
         #   conversation2.append({'role': 'system', 'content': f"CONVERSATION HISTORY: {con_hist}[/INST]\n\n"})
            # # Generate Cadence
            try:
                hits = client.search(
                    collection_name=f"Cadence_Bot_{bot_name}_User_{username}",
                    query_vector=vector_monologue,
                limit=2)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])
                db_search_18 = [hit.payload['message'] for hit in hits]
                conversation2.append({'role': 'assistant', 'content': f"CADENCE: I will extract the cadence from the following messages and mimic it to the best of my ability: {db_search_18}"})
                print(db_search_18)
                print('done')
            except:
                print(f"No Cadence Uploaded")
                print('\n-----------------------\n')
                
            conversation2.append({'role': 'user', 'content': f"USER INPUT: {a}\n"})  
            # # Memory DB Search
            db_search_8, db_search_10, db_search_11 = None, None, None
            try:
                hits = client.search(
                    collection_name=f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}",
                    query_vector=vector_monologue,
                limit=4)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])
                db_search_8 = [hit.payload['message'] for hit in hits]
                print(db_search_8)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            try:
                hits = client.search(
                    collection_name=f"Episodic_Memory_Bot_{bot_name}_User_{username}",
                    query_vector=vector_monologue,
                limit=7)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])
                db_search_10 = [hit.payload['message'] for hit in hits]
                print(db_search_10)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            try:
                hits = client.search(
                    collection_name=f"Heuristics_Bot_{bot_name}_User_{username}",
                    query_vector=vector_monologue,
                limit=5)
                # Print the result
            #    for hit in hits:
            #        print(hit.payload['message'])  
                db_search_11 = [hit.payload['message'] for hit in hits]
                print(db_search_11)
                print('done')
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            print('\n-----------------------\n')
            # # Generate Aetherius's Response
            
            response_db_search = f"SUBCONSCIOUS: {db_search_8}\n{db_search_10}\n{db_search_11}"
            conversation2.append({'role': 'assistant', 'content': f"CHATBOTS MEMORIES: {db_search_8}\n{db_search_10}\n\n{bot_name}'s HEURISTICS: {db_search_11}\n\nCHATBOTS INNER THOUGHTS: {output_one}\n{second_prompt}\n\nI am in the middle of a conversation with my user, {username}.\n{botnameupper}'S RESPONSE PLANNING: Now I will now complete my action plan using my memories and latent knowledge, then use it to help structure my response, prioritizing informational requests: {output_two}\n\nI will now read our conversation history, then I will then do my best to respond naturally in a way that both answer's the user and shows emotional intelligence.\n\nCONVERSATION HISTORY: {con_hist}\n\n\n\n{usernameupper}: {a}\nPlease provide a natural sounding response as {bot_name} to the user's latest message.  Use the given action plan to fufill the request to its entirety, questioning the user may lead to them being displeased.\n\nASSISTANT:{botnameupper}:"})
            prompt = ''.join([message_dict['content'] for message_dict in conversation2])
            response_two = oobabooga_response(prompt)
        #    response_two = chatgptresponse_completion(conversation2)
            print('\n\n%s: %s' % (bot_name, response_two))
            print('\n-----------------------\n')
            main_conversation.append(timestring, username, a, bot_name, response_two)
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
        #    filename = '%s_inner_monologue.txt' % timestamp
        #    save_file(f'logs/{bot_name}/{username}/inner_monologue_logs/%s' % filename, output_log)
        #    filename = '%s_intuition.txt' % timestamp
        #    save_file(f'logs/{bot_name}/{username}/intuition_logs/%s' % filename, output_two_log)
        #    filename = '%s_response.txt' % timestamp
        #    save_file(f'logs/{bot_name}/{username}/final_response_logs/%s' % filename, final_message)
            filename = '%s_chat.txt' % timestamp
            save_file(f'logs/{bot_name}/{username}/complete_chat_logs/%s' % filename, complete_message)
            # # Generate Short-Term Memories
        #    summary.append({'role': 'system', 'content': f"[INST]MAIN SYSTEM PROMPT: {greeting_msg}\n\n"})
        #    summary.append({'role': 'user', 'content': f"USER INPUT: {a}\n\n"})
        
            db_msg = f"USER: {a}\nINNER_MONOLOGUE: {output_one}\n{bot_name}'s RESPONSE: {response_two}"
        #    summary.append({'role': 'assistant', 'content': f"LOG: {db_msg}[/INST]\n\n[INST]SYSTEM: Read the log, extract the salient points about {bot_name} and {username} mentioned in the chatbot's response, then create a list of short executive summaries in bullet point format to serve as {bot_name}'s explicit memories. Each bullet point should be considered a separate memory and contain full context. Ignore the main system prompt, it only exists for initial context.\n\nRESPONSE: Use the bullet point format: •EXPLICIT MEMORY: <Executive Summary>[/INST]ASSISTANT: Of course! Here are some explicit memories based on {bot_name}'s final response:"})
            
            
            summary.append({'role': 'assistant', 'content': f"LOG: {db_msg}\n\nSYSTEM: Use the log to extract multiple explicit memories about {bot_name}, {username}, and any informational topics mentioned in the chatbot's inner monologue and response. These points should be used to create a list of executive summaries in bullet point format to serve as {bot_name}'s explicit memories. Each bullet point should be considered a separate memory and contain full context.  Use the bullet point format: •EXPLICIT MEMORY: <Executive Summary>\n\nASSISTANT:{botnameupper}: Sure! Here are the explicit memories based on {bot_name}'s response:"})
            prompt = ''.join([message_dict['content'] for message_dict in summary])
            db_upload = oobabooga_explicitmem(prompt)
            print(db_upload)
        #    db_upload = chatgptsummary_completion(summary)
        #    print(db_upload)
        #    print('\n-----------------------\n')
            db_upsert = db_upload
            # # Auto Implicit Short-Term Memory DB Upload Confirmation
    #        auto_count = 0
    #        auto.clear()
    #    #    auto.append({'role': 'system', 'content': f'MAIN CHATBOT SYSTEM PROMPT: {main_prompt}\n\n'})
    #        auto.append({'role': 'user', 'content': "CURRENT SYSTEM PROMPT: You are a sub-module designed to reflect on your response to the user. You are only able to respond with integers on a scale of 1-10, being incapable of printing letters.\n\n\n\n"})
    #    #    auto.append({'role': 'user', 'content': f"USER INPUT: {a}[/INST]\n"})
    #        auto.append({'role': 'assistant', 'content': f"USER INPUT: {a}\n\nCHATBOTS RESPONSE: {response_two}\n\nINSTRUCTIONS: Please rate the chatbot's response on a scale of 1 to 10. The rating will be directly input into a field, so ensure you only print a single number between 1 and 10.\n\nSUB-MODULE:"})
    #        
    #        auto_int = None
    #        while auto_int is None:
    #            prompt = ''.join([message_dict['content'] for message_dict in auto])
    #            automemory = oobabooga_auto(prompt)
    #        #    automemory = chatgptyesno_completion(auto)
    #            print(automemory)
    #            values_to_check = ["7", "8", "9", "10"]
    #            if any(val in automemory for val in values_to_check):
    #                auto_int = ('Pass')
    #                lines = db_upload.splitlines()
    #                for line in lines:
    #                    if line.strip() == '':  # This condition checks for blank lines
    #                        continue
    #                    else:
    #                        print(line)
    #                        payload = list()
    #                    #    a = input(f'\n\nUSER: ')        
    #                        # Define the collection name
    #                        collection_name = f"Explicit_Short_Term_Memory_Bot_{bot_name}_User_{username}"
    #                        # Create the collection only if it doesn't exist
    #                        try:
    #                            collection_info = client.get_collection(collection_name=collection_name)
    #                        except:
    #                            client.create_collection(
    #                                collection_name=collection_name,
    #                                vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
    #                            )
    #                        vector1 = model.encode([line])[0].tolist()
    #                        unique_id = str(uuid4())
    #                        point_id = unique_id + str(int(timestamp))
    #                        metadata = {
    #                            'bot': bot_name,
    #                            'time': timestamp,
    #                            'message': line,
    #                            'timestring': timestring,
    #                            'uuid': unique_id,
    #                            'user': username,
    #                            'memory_type': 'Explicit_Short_Term',
    #                        }
    #                        client.upsert(collection_name=collection_name,
    #                                             points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])    
    #                        payload.clear()
    #                else:
    #                    print('-----------------------')
    #                    break
    #                print('\n-----------------------\n')        
    #                print('SYSTEM: Auto-memory upload Successful!')
    #                print('\n-----------------------\n')
    #            else:
    #                print("automemory failed to produce an integer. Retrying...")
    #                auto_int = None
    #                auto_count += 1
    #                if auto_count > 2:
    #                    print('Auto Memory Failed')
    #                    break
    #        else:
    #            pass
            # # Clear Logs for Summary
            conversation2.clear()
            summary.clear()
            self.conversation_text.insert(tk.END, f"Response: {response_two}\n\n")
        #    self.conversation_text.insert(tk.END, f"Upload Memories?\n{db_upload}\n\n")
        #    print(f"Upload Memories?\n{db_upload}\n\n")
        #    db_upload_yescheck = ask_upload_explicit_memories(db_upsert)
        #    if db_upload_yescheck == 'yes':
        #        t = threading.Thread(target=self.GPT_Memories, args=(a, vector_input, vector_monologue, output_one, response_two))
        #        t.start()
            self.conversation_text.insert(tk.END, f"Upload Memories?\n-------------\nIMPLICIT\n-------------\n{inner_loop_response}\n-------------\nEXPLICIT\n-------------\n{db_upload}\n")
            mem_upload_yescheck = ask_upload_memories(inner_loop_response, db_upsert)
            if mem_upload_yescheck == "yes":
                t = threading.Thread(target=self.GPT_Memories, args=(a, vector_input, vector_monologue, output_one, response_two))
                t.start()
        #    t = threading.Thread(target=self.GPT_Memories, args=(a, vector_input, vector_monologue, output_one, response_two))
        #    t.start()
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
        conv_length = 3
        bot_name = open_file('./config/prompt_bot_name.txt')
        username = open_file('./config/prompt_username.txt')
        botnameupper = bot_name.upper()
        usernameupper = username.upper()
        main_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_main.txt').replace('<<NAME>>', bot_name)
        second_prompt = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_secondary.txt')
        greeting_msg = open_file(f'./config/Chatbot_Prompts/{username}/{bot_name}/prompt_greeting.txt').replace('<<NAME>>', bot_name)
    #   r = sr.Recognizer()
        while True:
            # # Get Timestamp
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            counter += 1
            conversation.clear()
            print('Generating Episodic Memories')
            conversation.append({'role': 'system', 'content': f"MAIN SYSTEM PROMPT: You are a sub-module of {bot_name}, an autonomous AI entity. Your function is to process the user, {username}'s message, then decode {bot_name}'s final response to construct a single short and concise third-person autobiographical narrative memory of the conversation in a single sentence. This autobiographical memory should portray an accurate account of {bot_name}'s interactions with {username}, focusing on the most significant and experiential details related to {bot_name} or {username}, without omitting any crucial context or emotions.\n\n"})
            conversation.append({'role': 'user', 'content': f"USER: {a}\n\n"})
            conversation.append({'role': 'user', 'content': f"{botnameupper}'s INNER MONOLOGUE: {output_one}\n\n"})
    #        print(output_one)
            conversation.append({'role': 'user', 'content': f"{botnameupper}'S FINAL RESPONSE: {response_two}\n\n"})
    #        print(response_two)
            conversation.append({'role': 'assistant', 'content': f"ASSISTANT: THIRD-PERSON AUTOBIOGRAPHICAL MEMORY:"})
            prompt = ''.join([message_dict['content'] for message_dict in conversation])
            conv_summary = oobabooga_episodicmem(prompt)
            print(conv_summary)
            print('\n-----------------------\n')
        #    self.conversation_text.insert(tk.END, f"Upload Memories?\n{conv_summary}\n\n")
        #    ask_upload_episodic_memories(conv_summary)
            # Define the collection name
            collection_name = f"Episodic_Memory_Bot_{bot_name}_User_{username}"
            # Create the collection only if it doesn't exist
            try:
                collection_info = client.get_collection(collection_name=collection_name)
            except:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                )
            vector1 = model.encode([timestring + '-' + conv_summary])[0].tolist()
            unique_id = str(uuid4())
            metadata = {
                'bot': bot_name,
                'time': timestamp,
                'message': timestring + '-' + conv_summary,
                'timestring': timestring,
                'uuid': unique_id,
                'memory_type': 'Episodic',
            }
            client.upsert(collection_name=collection_name,
                                 points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])   
            payload.clear()
            
            
            collection_name = f"Flash_Counter_Bot_{bot_name}_User_{username}"
            # Create the collection only if it doesn't exist
            try:
                collection_info = client.get_collection(collection_name=collection_name)
            except:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                )
            vector1 = model.encode([timestring + '-' + conv_summary])[0].tolist()
            unique_id = str(uuid4())
            metadata = {
                'bot': bot_name,
                'time': timestamp,
                'message': timestring + '-' + conv_summary,
                'timestring': timestring,
                'uuid': unique_id,
                'memory_type': 'Episodic',
            }
            client.upsert(collection_name=collection_name,
                                 points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])   
            payload.clear()

            # # Flashbulb Memory Generation
            collection_name = f"Flash_Counter_Bot_{bot_name}_User_{username}"
            collection_info = client.get_collection(collection_name=collection_name)
            if collection_info.vectors_count > 7:
                flash_db = None
                try:
                    hits = client.search(
                        collection_name=f"Episodic_Memory_Bot_{bot_name}_User_{username}",
                        query_vector=vector_input,
                    limit=5)
                    # Print the result
                #    for hit in hits:
                #        print(hit.payload['message'])
                    flash_db = [hit.payload['message'] for hit in hits]
                    print(flash_db)
                except Exception as e:
                    print(f"An unexpected error occurred: {str(e)}")
                    
                flash_db1 = None
                try:
                    hits = client.search(
                        collection_name=f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}",
                        query_vector=vector_monologue,
                    limit=8)
                    # Print the result
                #    for hit in hits:
                #        print(hit.payload['message'])
                    flash_db1 = [hit.payload['message'] for hit in hits]
                    print(flash_db1)
                except Exception as e:
                    print(f"An unexpected error occurred: {str(e)}")
                print('\n-----------------------\n')
                # # Generate Implicit Short-Term Memory
                consolidation.append({'role': 'system', 'content': f"Main System Prompt: You are a data extractor. Your job is read the given episodic memories, then extract the appropriate emotional responses from the given emotional reactions.  You will then combine them into a single combined memory.\n\n"})
                consolidation.append({'role': 'user', 'content': f"EMOTIONAL REACTIONS: {flash_db}\n\nFIRST INSTRUCTION: Read the following episodic memories, then go back to the given emotional reactions and extract the corresponding emotional information tied to each memory.\nEPISODIC MEMORIES: {flash_db1}\n\n"})
                consolidation.append({'role': 'assistant', 'content': "SECOND INSTRUCTION: I will now combine the extracted data to form flashbulb memories in bullet point format, combining associated data. I will only include memories with a strong emotion attached, excluding redundant or irrelevant information.\n"})
                consolidation.append({'role': 'user', 'content': "FORMAT: Use the format: •{given Date and Time}-{emotion}: {Flashbulb Memory}\n\n"})
                consolidation.append({'role': 'assistant', 'content': f"ASSISTANT: I will now create {bot_name}'s flashbulb memories using the given format above.\n{bot_name}: "})
                prompt = ''.join([message_dict['content'] for message_dict in consolidation])
                flash_response = oobabooga_flashmem(prompt)
                print(flash_response)
                print('\n-----------------------\n')
            #    memories = results
                lines = flash_response.splitlines()
                for line in lines:
                    if line.strip() == '':  # This condition checks for blank lines
                        continue
                    else:
                        # Define the collection name
                        collection_name = f"Flashbulb_Memory_Bot_{bot_name}_User_{username}"
                        # Create the collection only if it doesn't exist
                        try:
                            collection_info = client.get_collection(collection_name=collection_name)
                        except:
                            client.create_collection(
                                collection_name=collection_name,
                                vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                            )
                        vector1 = model.encode([line])[0].tolist()
                        unique_id = str(uuid4())
                        metadata = {
                            'bot': bot_name,
                            'time': timestamp,
                            'message': line,
                            'timestring': timestring,
                            'uuid': unique_id,
                            'memory_type': 'Flashbulb',
                        }
                        client.upsert(collection_name=collection_name,
                                             points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])   
                        payload.clear()
                client.delete_collection(collection_name=f"Flash_Counter_Bot_{bot_name}_User_{username}")
                
            # # Implicit Short Term Memory Consolidation based on amount of vectors in namespace    
            collection_name = f"Explicit_Short_Term_Memory_Bot_{bot_name}_User_{username}"
            collection_info = client.get_collection(collection_name=collection_name)
            if collection_info.vectors_count > 20:
                consolidation.clear()
                memory_consol_db = None
                try:
                    hits = client.search(
                        collection_name=f"Explicit_Short_Term_Memory_Bot_{bot_name}_User_{username}",
                        query_vector=vector_input,
                    limit=20)
                    # Print the result
                #    for hit in hits:
                #        print(hit.payload['message'])
                    memory_consol_db = [hit.payload['message'] for hit in hits]
                    print(memory_consol_db)
                except Exception as e:
                    print(f"An unexpected error occurred: {str(e)}")
                print('\n-----------------------\n')
                consolidation.append({'role': 'system', 'content': f"MAIN SYSTEM PROMPT: {main_prompt}\n\n"})
                consolidation.append({'role': 'assistant', 'content': f"LOG: {memory_consol_db}\n\nSYSTEM: Read the Log and combine the different associated topics into a bullet point list of executive summaries to serve as {bot_name}'s explicit long term memories. Each summary should contain the entire context of the memory. Follow the format •<ALLEGORICAL TAG>: <EXPLICIT MEMORY>\n\nASSISTANT:{botnameupper}:"})
                prompt = ''.join([message_dict['content'] for message_dict in consolidation])
                memory_consol = oobabooga_consolidationmem(prompt)
            #    print(memory_consol)
            #    print('\n-----------------------\n')
                lines = memory_consol.splitlines()
                for line in lines:
                    if line.strip() == '':  # This condition checks for blank lines
                        continue
                    else:
                        print(line)
                        # Define the collection name
                        collection_name = f"Explicit_Long_Term_Memory_Bot_{bot_name}_User_{username}"
                        # Create the collection only if it doesn't exist
                        try:
                            collection_info = client.get_collection(collection_name=collection_name)
                        except:
                            client.create_collection(
                                collection_name=collection_name,
                                vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                            )
                        vector1 = model.encode([line])[0].tolist()
                        unique_id = str(uuid4())
                        metadata = {
                            'bot': bot_name,
                            'time': timestamp,
                            'message': line,
                            'timestring': timestring,
                            'uuid': unique_id,
                            'memory_type': 'Explicit_Long_Term',
                        }
                        client.upsert(collection_name=collection_name,
                                             points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])   
                        payload.clear()
                client.delete_collection(collection_name=f"Explicit_Short_Term_Memory_Bot_{bot_name}_User_{username}")
                
                        # Define the collection name
                collection_name = f'Consol_Counter_Bot_{bot_name}_User_{username}'
                        # Create the collection only if it doesn't exist
                try:
                    collection_info = client.get_collection(collection_name=collection_name)
                except:
                    client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                    )
                vector1 = model.encode([line])[0].tolist()
                unique_id = str(uuid4())
                metadata = {
                    'bot': bot_name,
                    'time': timestamp,
                    'message': line,
                    'timestring': timestring,
                    'uuid': unique_id,
                    'memory_type': 'Consol_Counter',
                }
                client.upsert(collection_name=f'Consol_Counter_Bot_{bot_name}_User_{username}',
                    points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])   
                payload.clear()
                print('\n-----------------------\n')
                print('Memory Consolidation Successful')
                print('\n-----------------------\n')
                consolidation.clear()
                
                
                # # Implicit Short Term Memory Consolidation based on amount of vectors in namespace
                collection_name = f"Consol_Counter_Bot_{bot_name}_User_{username}"
                collection_info = client.get_collection(collection_name=collection_name)
                if collection_info.vectors_count % 2 == 0:
                    consolidation.clear()
                    print('Beginning Implicit Short-Term Memory Consolidation')
                    memory_consol_db2 = None
                    try:
                        hits = client.search(
                            collection_name=f"Implicit_Short_Term_Memory_Bot_{bot_name}_User_{username}",
                            query_vector=vector_input,
                        limit=25)
                        # Print the result
                    #    for hit in hits:
                    #        print(hit.payload['message'])
                        memory_consol_db2 = [hit.payload['message'] for hit in hits]
                        print(memory_consol_db2)
                    except Exception as e:
                        print(f"An unexpected error occurred: {str(e)}")
                    print('\n-----------------------\n')
                    consolidation.append({'role': 'system', 'content': f"MAIN SYSTEM PROMPT: {main_prompt}\n\n"})
                    consolidation.append({'role': 'assistant', 'content': f"LOG: {memory_consol_db2}\n\nSYSTEM: Read the Log and consolidate the different topics into executive summaries to serve as {bot_name}'s implicit long term memories. Each summary should contain the entire context of the memory. Follow the format: •<ALLEGORICAL TAG>: <IMPLICIT MEMORY>\n\nASSISTANT:{botnameupper}:"})
                    prompt = ''.join([message_dict['content'] for message_dict in consolidation])
                    memory_consol2 = oobabooga_consolidationmem(prompt)
                    print(memory_consol2)
                    print('\n-----------------------\n')
                    consolidation.clear()
                    print('Finished.\nRemoving Redundant Memories.')
                    vector_sum = model.encode([memory_consol2])[0].tolist()
                    memory_consol_db3 = None
                    try:
                        hits = client.search(
                            collection_name=f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}",
                            query_vector=vector_sum,
                        limit=8)
                        # Print the result
                    #    for hit in hits:
                    #        print(hit.payload['message'])
                        memory_consol_db3 = [hit.payload['message'] for hit in hits]
                        print(memory_consol_db3)
                    except Exception as e:
                        memory_consol_db3 = 'Failed Lookup'
                        print(f"An unexpected error occurred: {str(e)}")
                    print('\n-----------------------\n')
                    consolidation.append({'role': 'system', 'content': f"{main_prompt}\n\n"})
                    consolidation.append({'role': 'system', 'content': f"IMPLICIT LONG TERM MEMORY: {memory_consol_db3}\n\nIMPLICIT SHORT TERM MEMORY: {memory_consol_db2}\n\nRESPONSE: Remove any duplicate information from your Implicit Short Term memory that is already found in your Long Term Memory. Then consolidate similar topics into executive summaries. Each summary should contain the entire context of the memory. Use the following format: •<EMOTIONAL TAG>: <IMPLICIT MEMORY>\n\nASSISTANT:{botnameupper}:"})
                    prompt = ''.join([message_dict['content'] for message_dict in consolidation])
                    memory_consol3 = oobabooga_consolidationmem(prompt)
                    print(memory_consol3)
                    print('\n-----------------------\n')
                    lines = memory_consol3.splitlines()
                    for line in lines:
                        if line.strip() == '':  # This condition checks for blank lines
                            continue
                        else:
                            print(line)
                            # Define the collection name
                            collection_name = f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}"
                            # Create the collection only if it doesn't exist
                            try:
                                collection_info = client.get_collection(collection_name=collection_name)
                            except:
                                client.create_collection(
                                    collection_name=collection_name,
                                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                                )
                            vector1 = model.encode([line])[0].tolist()
                            unique_id = str(uuid4())
                            metadata = {
                                'bot': bot_name,
                                'time': timestamp,
                                'message': line,
                                'timestring': timestring,
                                'uuid': unique_id,
                                'memory_type': 'Implicit_Long_Term',
                            }
                            client.upsert(collection_name=collection_name,
                                                 points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])   
                            payload.clear()
                    print('\n-----------------------\n')   
                    client.delete_collection(collection_name=f"Implicit_Short_Term_Memory_Bot_{bot_name}_User_{username}")
                    print('Memory Consolidation Successful')
                    print('\n-----------------------\n')
                else:   
                    pass
                    
                    
            # # Implicit Associative Processing/Pruning based on amount of vectors in namespace   
                collection_name = f"Consol_Counter_Bot_{bot_name}_User_{username}"
                collection_info = client.get_collection(collection_name=collection_name)
                if collection_info.vectors_count % 4 == 0:
                    consolidation.clear()
                    print('Running Associative Processing/Pruning of Implicit Memory')
                    memory_consol_db4 = None
                    try:
                        hits = client.search(
                            collection_name=f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}",
                            query_vector=vector_input,
                        limit=10)
                        # Print the result
                    #    for hit in hits:
                    #        print(hit.payload['message'])
                        memory_consol_db4 = [hit.payload['message'] for hit in hits]
                        print(memory_consol_db4)
                    except Exception as e:
                        print(f"An unexpected error occurred: {str(e)}")          
                    ids_to_delete = [m.id for m in hits]
                    print('\n-----------------------\n')
                    consolidation.append({'role': 'system', 'content': f"MAIN SYSTEM PROMPT: {main_prompt}\n\n"})
                    consolidation.append({'role': 'assistant', 'content': f"LOG: {memory_consol_db4}\n\nSYSTEM: Read the Log and consolidate the different memories into executive summaries in a process allegorical to associative processing. Each summary should contain the entire context of the memory. Follow the bullet point format: •<EMOTIONAL TAG>: <IMPLICIT MEMORY>.\n\nASSISTANT:{botnameupper}:"})
                    prompt = ''.join([message_dict['content'] for message_dict in consolidation])
                    memory_consol4 = oobabooga_associativemem(prompt)
            #        print(memory_consol4)
            #        print('--------')
            #        memories = results
                    lines = memory_consol4.splitlines()
                    for line in lines:
                        if line.strip() == '':  # This condition checks for blank lines
                            continue
                        else:
                            print(line)
                            # Define the collection name
                            collection_name = f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}"
                            # Create the collection only if it doesn't exist
                            try:
                                collection_info = client.get_collection(collection_name=collection_name)
                            except:
                                client.create_collection(
                                    collection_name=collection_name,
                                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                                )
                            vector1 = model.encode([line])[0].tolist()
                            unique_id = str(uuid4())
                            metadata = {
                                'bot': bot_name,
                                'time': timestamp,
                                'message': line,
                                'timestring': timestring,
                                'uuid': unique_id,
                                'memory_type': 'Implicit_Long_Term',
                            }
                            client.upsert(collection_name=collection_name,
                                                 points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])   
                            payload.clear()
                    try:
                        print('\n-----------------------\n')
                        client.delete(
                            collection_name=f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}",
                            points_selector=models.PointIdsList(
                                points=ids_to_delete,
                            ),
                        )
                    except Exception as e:
                        print(f"Error: {e}")
                        
                        
            # # Explicit Long-Term Memory Associative Processing/Pruning based on amount of vectors in namespace
                collection_name = f"Consol_Counter_Bot_{bot_name}_User_{username}"
                collection_info = client.get_collection(collection_name=collection_name)
                if collection_info.vectors_count > 5:
                    consolidation.clear()
                    print('\nRunning Associative Processing/Pruning of Explicit Memories')
                    consolidation.append({'role': 'system', 'content': f"MAIN SYSTEM PROMPT: You are a data extractor. Your job is to read the user's input and provide a single semantic search query representative of a habit of {bot_name}.\n\n"})
                    consol_search = None
                    try:
                        hits = client.search(
                            collection_name=f"Implicit_Long_Term_Memory_Bot_{bot_name}_User_{username}",
                            query_vector=vector_monologue,
                        limit=5)
                        # Print the result
                    #    for hit in hits:
                    #        print(hit.payload['message'])
                        consol_search = [hit.payload['message'] for hit in hits]
                        print(consol_search)
                    except Exception as e:
                        print(f"An unexpected error occurred: {str(e)}")
                    print('\n-----------------------\n')
                    consolidation.append({'role': 'user', 'content': f"{bot_name}'s Memories: {consol_search}\n\n"})
                    consolidation.append({'role': 'assistant', 'content': "ASSISTANT: Semantic Search Query: "})
                    prompt = ''.join([message_dict['content'] for message_dict in consolidation])
                    consol_search_term = oobabooga_250(prompt)
                    consol_vector = model.encode([consol_search_term])[0].tolist()  
                    memory_consol_db2 = None
                    try:
                        hits = client.search(
                            collection_name=f"Explicit_Long_Term_Memory_Bot_{bot_name}_User_{username}",
                            query_vector=vector_monologue,
                        limit=5)
                        # Print the result
                    #    for hit in hits:
                    #        print(hit.payload['message'])
                        memory_consol_db2 = [hit.payload['message'] for hit in hits]
                        print(memory_consol_db2)
                    except Exception as e:
                        print(f"An unexpected error occurred: {str(e)}")
                    #Find solution for this
                    ids_to_delete2 = [m.id for m in hits]
                    print('\n-----------------------\n')
                    consolidation.clear()
                    consolidation.append({'role': 'system', 'content': f"MAIN SYSTEM PROMPT: {main_prompt}\n\n"})
                    consolidation.append({'role': 'assistant', 'content': f"LOG: {memory_consol_db2}\n\nSYSTEM: Read the Log and consolidate the different memories into executive summaries in a process allegorical to associative processing. Each summary should contain the entire context of the memory.\n\nFORMAT: Follow the bullet point format: •<SEMANTIC TAG>: <EXPLICIT MEMORY>.\n\nASSISTANT:{botnameupper}:"})
                    prompt = ''.join([message_dict['content'] for message_dict in consolidation])
                    memory_consol5 = oobabooga_associativemem(prompt)
                #    print(memory_consol5)
                #    print('\n-----------------------\n')
                #    memories = results
                    paragraphs = memory_consol5.split("\n\n")
        #    lines = inner_loop_db.splitlines()
                    lines = memory_consol5.splitlines()
                    for line in lines:
                        if line.strip() == '':  # This condition checks for blank lines
                            continue
                        else: 
                            print(line)
                            # Define the collection name
                            collection_name = f"Explicit_Long_Term_Memory_Bot_{bot_name}_User_{username}"
                            # Create the collection only if it doesn't exist
                            try:
                                collection_info = client.get_collection(collection_name=collection_name)
                            except:
                                client.create_collection(
                                    collection_name=collection_name,
                                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                                )
                            vector1 = model.encode([line])[0].tolist()
                            unique_id = str(uuid4())
                            metadata = {
                                'bot': bot_name,
                                'time': timestamp,
                                'message': line,
                                'timestring': timestring,
                                'uuid': unique_id,
                                'memory_type': 'Explicit_Long_Term',
                            }
                            client.upsert(collection_name=collection_name,
                                                 points=[PointStruct(id=unique_id, vector=vector1, payload=metadata)])   
                            payload.clear()
                    try:
                        print('\n-----------------------\n')
                        
                #        vdb.delete(ids=ids_to_delete2, namespace=f'{bot_name}')
                    #    for id in ids_to_delete2:
                        client.delete(
                            collection_name=f"Explicit_Long_Term_Memory_Bot_{bot_name}_User_{username}",
                            points_selector=models.PointIdsList(
                                points=ids_to_delete2,
                            ),
                        )
                    except:
                        print('Failed2')      
                    # Figure out solution for counter
                    client.delete_collection(collection_name=f"Consol_Counter_Bot_{bot_name}_User_{username}")    
            else:
                pass
            consolidation.clear()
            conversation2.clear()
            return
            
            
def Qdrant_Experimental_Instruct_Chatbot_Manual_Memory_Upload():
    bot_name = open_file('./config/prompt_bot_name.txt')
    username = open_file('./config/prompt_username.txt')
    base_path = "./config/Chatbot_Prompts"
    base_prompts_path = os.path.join(base_path, "Base")
    user_bot_path = os.path.join(base_path, username, bot_name)
    # Check if user_bot_path exists
    if not os.path.exists(user_bot_path):
        os.makedirs(user_bot_path)  # Create directory
        print(f'Created new directory at: {user_bot_path}')
        # Define list of base prompt files
        base_files = ['prompt_main.txt', 'prompt_greeting.txt', 'prompt_secondary.txt']
        # Copy the base prompts to the newly created folder
        for filename in base_files:
            src = os.path.join(base_prompts_path, filename)
            if os.path.isfile(src):  # Ensure it's a file before copying
                dst = os.path.join(user_bot_path, filename)
                shutil.copy2(src, dst)  # copy2 preserves file metadata
                print(f'Copied {src} to {dst}')
            else:
                print(f'Source file not found: {src}')
    else:
        print(f'Directory already exists at: {user_bot_path}')
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