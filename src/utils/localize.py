from transformers import MarianMTModel, MarianTokenizer
import os
import json
import typing as t
import re

from utils.get_resources import get_resource_file


ORIGINAL_MESG_POSTFIX:str = '_mesg_original.json'
GEN_MESG_POSTFIX:str = '_mesg_gen.json'
DEFAULT_LANG:str = 'en'


def translate(model: MarianMTModel, tokenizer: MarianTokenizer, text: str) -> str:
    sentences = re.split(r'([?!.\n])', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    tokenized_text = tokenizer([text], return_tensors='pt')
    translation = model.generate(**tokenized_text)
    translated_text = tokenizer.decode(translation[0], skip_special_tokens=True)
    return translated_text

def auto_localize(lang: str, messages: dict) -> dict:
    model_name = 'Helsinki-NLP/opus-mt-en-' + lang
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    
    res = messages.copy()

    def translate_dict_recursive(d: dict):
        for k, v in d.items():
            if type(v) == dict:
                translate_dict_recursive(v)
            else:
                d[k] = translate(model, tokenizer, v)

    translate_dict_recursive(res)
    return res

def load_language(lang: str, write_file:bool=True) -> dict:
    data_path = str(get_resource_file("data/"))  + '/'
    o_path, g_path = map(lambda x: data_path + lang + x, 
                         [ORIGINAL_MESG_POSTFIX, GEN_MESG_POSTFIX])
    if os.path.exists(o_path):
        with open(o_path, 'r') as f:
            messages = json.load(f)
    elif os.path.exists(g_path):
        with open(g_path, 'r') as f:
            messages = json.load(f)
    else:
        with open(data_path + DEFAULT_LANG + ORIGINAL_MESG_POSTFIX, 'r') as s:
            messages = auto_localize(lang, json.load(s)) 
        if write_file:
            with open(g_path, 'w') as f:
                json.dump(messages, f, indent=4, ensure_ascii=False)
    return messages
