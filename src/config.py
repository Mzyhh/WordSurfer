from configparser import ConfigParser
from gensim.models import KeyedVectors
import gensim.downloader as api
import typing as t
import os
import gzip
import shutil
from dataclasses import dataclass
import json

from utils.get_resources import get_resource_file


@dataclass(frozen=True)
class Config:
    language: str
    model: KeyedVectors
    vocabulary: t.List[str]
    messages: t.Dict

    int_filepath: str

    n_options: int


def launch() -> Config:
    """Load embeddings if needed unpack them and do other important stuff."""
    config = ConfigParser()
    config.read(str(get_resource_file('config.ini')))

    gz_path = api.load(str(config['General']['embeddings']), return_path=True)

    txt_path = os.path.splitext(gz_path)[0] + ".txt"
    if not os.path.exists(txt_path):
        print("Extracting some very important files...")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(txt_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    data_path = str(get_resource_file("data/"))  + '/'
    with open(data_path + str(config['General']['language']) + '_vocab_original.txt', 'r') as voc:
        vocab = set(voc.read().split('\n'))

    result_file = data_path + 'glove-twitter-100' + ".bin"
    if not os.path.exists(result_file):
        print("Transforming one substance to another, may take a while...")
        model = KeyedVectors.load_word2vec_format(txt_path, binary=False)
        clean_words = {word: model[word] for word in model.key_to_index
                       if word in vocab and word.isalpha()}
        model = KeyedVectors(vector_size=model.vector_size)
        model.add_vectors(keys=list(clean_words.keys()), weights=list(clean_words.values()))
        model.save(result_file)
    model = KeyedVectors.load(result_file, mmap='r') 

    vocab = [word for word in vocab if word in model.key_to_index]

    with open(data_path + str(config['General']['language']) + "_mesg_original.json", 'r') as f:
        mesg = json.load(f)

    return Config(
        language=config['General']['language'],
        model=model,
        messages=mesg,
        vocabulary=vocab,
        int_filepath=config['Playground']['int_file'],
        n_options=int(config['Quiz']['n_options'])
    )
