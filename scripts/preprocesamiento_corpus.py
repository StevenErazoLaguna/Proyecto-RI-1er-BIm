#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preprocesamiento_programmers.py

NEW

Limpia y preprocesa el corpus del dataset de programación. Aplica:
- Limpieza de texto
- Tokenización alfanumérica
- Mapeo de números a <NUM>
- Eliminación de stopwords (inglés + dominio programación)
- Lematización
- Filtro por frecuencia de documento (DF)
"""

import os
import re
import argparse
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import regexp_tokenize
from sklearn.feature_extraction.text import CountVectorizer

INPUT_DIR = r"C:\Users\roble\OneDrive\Documentos\GitHub\Proyecto-RI-1er-BIm\corpus2"
OUTPUT_DIR = r"C:\Users\roble\OneDrive\Documentos\GitHub\Proyecto-RI-1er-BIm\corpus2_clean"

REGEX_PATTERN = r"[a-z0-9]+"
STOPWORD_LANG = "english"

# Stopwords del dominio de programación
DOMAIN_STOPWORDS = {
    "code", "function", "variable", "class", "int", "string", "print", "value", 
    "return", "python", "java", "error", "output", "input", "type", "method",
    "true", "false", "null", "void", "main", "line", "run", "compiler", "loop",
    "char", "name", "data", "array", "object", "args", "console", "debug"
}

MIN_DF = 2
MAX_DF_RATIO = 0.9

def inicializar_nltk():
    for pkg in ("punkt", "stopwords", "wordnet"):
        try:
            nltk.data.find(f"tokenizers/{pkg}")
        except LookupError:
            nltk.download(pkg)

def limpiar_texto(texto: str) -> str:
    texto = re.sub(r"\b\d+(?:\.\d+)?\b", " <NUM> ", texto)
    texto = re.sub(r"http\S+", " ", texto)
    texto = re.sub(r"[^A-Za-z0-9\s]", " ", texto)
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def construir_vocabulario(corpus_texts):
    vect = CountVectorizer(min_df=MIN_DF, max_df=MAX_DF_RATIO, token_pattern=REGEX_PATTERN)
    vect.fit(corpus_texts)
    return set(vect.get_feature_names_out())

def procesar_texto(texto: str, vocab_permitido: set,
                   stopwords_set: set,
                   lemmatizer: WordNetLemmatizer) -> str:
    tokens = regexp_tokenize(texto, pattern=REGEX_PATTERN)
    tokens = [t for t in tokens if t and t in vocab_permitido and t not in stopwords_set]
    lemmas = [lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(lemmas)

def main(input_dir: str, output_dir: str):
    inicializar_nltk()
    os.makedirs(output_dir, exist_ok=True)

    sw_set = set(stopwords.words(STOPWORD_LANG)) | DOMAIN_STOPWORDS
    lemmatizer = WordNetLemmatizer()

    archivos = [f for f in os.listdir(input_dir) if f.lower().endswith('.txt')]
    total = len(archivos)
    print(f"Se encontraron {total} archivos, preparando DF-filter...")

    docs_crudos = []
    for nombre in archivos:
        with open(os.path.join(input_dir, nombre), encoding='utf-8') as f:
            docs_crudos.append(limpiar_texto(f.read()))

    vocab = construir_vocabulario(docs_crudos)
    print(f"Vocabulario filtrado: {len(vocab)} términos permitidos.")

    for idx, nombre in enumerate(archivos, 1):
        texto_crudo = limpiar_texto(open(os.path.join(input_dir, nombre), encoding='utf-8').read())
        texto_procesado = procesar_texto(texto_crudo, vocab, sw_set, lemmatizer)
        base, _ = os.path.splitext(nombre)
        out_path = os.path.join(output_dir, f"{base}_clean.txt")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(texto_procesado)
        if idx % 500 == 0 or idx == total:
            print(f"Procesados {idx}/{total} archivos ({(idx/total)*100:.1f}%)")

    print("Preprocesamiento completado para corpus de programación.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default=INPUT_DIR)
    parser.add_argument('--output_dir', default=OUTPUT_DIR)
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)
