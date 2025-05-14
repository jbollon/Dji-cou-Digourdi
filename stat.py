import re
from collections import defaultdict, Counter

# === CONFIGURA QUI I TUOI FILE .TEX ===
tex_files = [
   "2009.tex",
   "2010.tex",
   "2011.tex",
   "2012.tex",
   "2013.tex",
   "2014.tex",
   "2015.tex",
   "2016.tex",
   "2017.tex",
   "2018.tex",
   "2019.tex"
]

# === CONFIGURA PAROLE DA ESCLUDERE (stopwords) ===
stopwords = {
    "que", "eun", "ouè", "vouè", "avouì", "eunna", "bièn", "senque", "ara",
    "lèi", "can", "maque", "seuilla", "seutta", "comme", "euncó", "adón",
    "aprì", "fran", "todzor", "tcheu", "dou", "comèn", "totte", "oueu",
    "tcheutte", "iaou", "dza", "bon", "cou", "pequé", "ren", "djeusto",
    "sise", "eugn", "deun", "tan", "mimo", "salla", "dzen", "qui",
    "deu", "sen", "son", "fièn", "vou"  #verbi 
}

# === CONFIGURA MINIMA LUNGHEZZA DELLE PAROLE ===
min_word_length = 3  # Ignora parole più corte di 3 lettere

def latex_accenti_to_utf8(text):
    replacements = {
        r"\\`a": "à", r"\\'a": "á", r'\\"a': "ä",
        r"\\`e": "è", r"\\'e": "é", r'\\"e': "ë",
        r"\\`i": "ì", r"\\'i": "í", r'\\"i': "ï",
        r"\\`o": "ò", r"\\'o": "ó", r'\\"o': "ö",
        r"\\`u": "ù", r"\\'u": "ú", r'\\"u': "ü",
        r"\\`A": "À", r"\\'A": "Á", r'\\"A': "Ä",
        r"\\`E": "È", r"\\'E": "É", r'\\"E': "Ë",
        r"\\`I": "Ì", r"\\'I": "Í", r'\\"I': "Ï",
        r"\\`O": "Ò", r"\\'O": "Ó", r'\\"O': "Ö",
        r"\\`U": "Ù", r"\\'U": "Ú", r'\\"U': "Ü",
    }
    for latex, utf8 in replacements.items():
        text = re.sub(latex, utf8, text)
    return text


def clean_tex_content(content):
    # Rimuove comandi tipo \StageDir{...}
    content = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', content)
    # Rimuove comandi tipo \command
    content = re.sub(r'\\[a-zA-Z]+', '', content)
    return content

def extract_words(content):
    content = clean_tex_content(content)
    content = latex_accenti_to_utf8(content)
    words = re.findall(r'\b\w+\b', content.lower(), flags=re.UNICODE)
    #words = re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', content.lower())
    filtered = [
        w for w in words
        if len(w) >= min_word_length and w not in stopwords
    ]
    return filtered

# === CONTEGGIO PAROLE ===
cumulative_counter = Counter()

for filename in tex_files:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            words = extract_words(content)
            word_count = Counter(words)
            cumulative_counter.update(word_count)
    except FileNotFoundError:
        print(f"[!] File non trovato: {filename}")

# === TOP 10 PAROLE ===
top_words = cumulative_counter.most_common(20)

# === OUTPUT IN FILE LATEX ===
with open("stat.tex", "w", encoding="utf-8") as out:
    out.write(r"""
\paragraph*{Top 10 parole più frequenti (escluse parole brevi e comuni)}

\begin{tabular}{ll}
\toprule
\textbf{Parola} & \textbf{Frequenza} \\
\midrule
""")
    for word, count in top_words:
        out.write(f"{word} & {count} \\\\\n")
    out.write(r"""\bottomrule
\end{tabular}

""")

print("[✓] File 'stat.tex' generato con successo.")
