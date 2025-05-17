import os
import re
from collections import defaultdict

# Lista dei file TeX
tex_files = [
    "2009.tex", "2010.tex", "2011.tex", "2012.tex", "2013.tex",
    "2014.tex", "2015.tex", "2016.tex", "2018.tex", "2019.tex"
]

# Funzione per normalizzare accenti LaTeX, inclusi formati \"e e \"{e}
def normalize_latex_accents(text):
    replacements = {
        r"\\`a": "à", r"\\'a": "á", r"\\\"a": "ä", r"\\\"\{a\}": "ä",
        r"\\`e": "è", r"\\'e": "é", r"\\\"e": "ë", r"\\\"\{e\}": "ë",
        r"\\`i": "ì", r"\\'i": "í", r"\\\"i": "ï", r"\\\"\{i\}": "ï",
        r"\\`o": "ò", r"\\'o": "ó", r"\\\"o": "ö", r"\\\"\{o\}": "ö",
        r"\\`u": "ù", r"\\'u": "ú", r"\\\"u": "ü", r"\\\"\{u\}": "ü",
        r"\\`A": "À", r"\\'A": "Á", r"\\\"A": "Ä", r"\\\"\{A\}": "Ä",
        r"\\`E": "È", r"\\'E": "É", r"\\\"E": "Ë", r"\\\"\{E\}": "Ë",
        r"\\`I": "Ì", r"\\'I": "Í", r"\\\"I": "Ï", r"\\\"\{I\}": "Ï",
        r"\\`O": "Ò", r"\\'O": "Ó", r"\\\"O": "Ö", r"\\\"\{O\}": "Ö",
        r"\\`U": "Ù", r"\\'U": "Ú", r"\\\"U": "Ü", r"\\\"\{U\}": "Ü",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    return text

# Pattern per Character con argomenti annidati e per name/nameF
character_full_pattern = re.compile(
    r'\\Character(?:\[[^\]]*\])?'      # [opzionale]
    r'\{([^\}]*)\}'                       # arg1 (ignorato)
    r'\{([^\}]*)\}'                       # arg2 = macro
    r'\{([^\}]*)\}'                       # arg3 (ignorato)
    r'\{((?:[^{}]+|\{[^}]*\})*)\}'       # arg4 = descrizione
)
name_pattern = re.compile(r'\\nameF?\{([^\}]+)\}')
direct_pattern = re.compile(r'\\direct\{.*?\}')
title_pattern = re.compile(r'\\title\{([^\}]+)\}')

# Strutture dati per le statistiche
actor_stats = defaultdict(lambda: {"pieces": set(), "lines": 0, "words": 0})
actor_names_display = {}  # normalizzato -> display
piece_stats = {}

# Parsing dei file
for filename in tex_files:
    if not os.path.exists(filename):
        continue
    with open(filename, 'r', encoding='utf-8') as f:
        raw = f.read()
    # Normalizza accenti in tutto il contenuto
    content = normalize_latex_accents(raw)
    # Estrai titolo
    m_title = title_pattern.search(content)
    title = m_title.group(1).strip() if m_title else filename

    # Mappa macro -> attore
    character_map = {}
    for m in character_full_pattern.finditer(content):
        macro = m.group(2)
        desc = m.group(4)
        m_name = name_pattern.search(desc)
        if not m_name:
            continue
        raw_name = m_name.group(1)
        display_name = normalize_latex_accents(raw_name).strip()
        normalized = display_name.lower()
        character_map[macro] = normalized
        actor_names_display[normalized] = display_name

    # Contatori per la pièce
    piece_lines = 0
    piece_words = 0
    actor_lines = defaultdict(int)
    actor_words = defaultdict(int)

    # Conta battute e parole
    for macro, actor in character_map.items():
        speak_pat = re.compile(r'\\' + re.escape(macro) + r'speaks\b')
        for sp in speak_pat.finditer(content):
            piece_lines += 1
            actor_stats[actor]['lines'] += 1
            actor_stats[actor]['pieces'].add(title)
            actor_lines[actor] += 1
            # Estrai testo dopo speaks
            start = sp.end()
            snippet = content[start:start+2000]
            m_next = re.search(r'\\\w+speaks\b', snippet)
            block = snippet[:m_next.start()] if m_next else snippet
            block = direct_pattern.sub('', block)
            words = re.findall(r'\b\w+\b', block)
            cnt = len(words)
            actor_stats[actor]['words'] += cnt
            actor_words[actor] += cnt
            piece_words += cnt

    # Attori chiave per la pièce
    mostl = max(actor_lines.items(), key=lambda x: x[1])[0] if actor_lines else '—'
    mostw = max(actor_words.items(), key=lambda x: x[1])[0] if actor_words else '—'
    piece_stats[title] = {'lines': piece_lines, 'words': piece_words,
                          'most_lines_actor': mostl,
                          'most_words_actor': mostw}

# Ordinamento
lines_sorted = sorted(actor_stats.items(), key=lambda x: x[1]['lines'], reverse=True)
words_sorted = sorted(actor_stats.items(), key=lambda x: x[1]['words'], reverse=True)
pieces_sorted = sorted(actor_stats.items(), key=lambda x: len(x[1]['pieces']), reverse=True)

# Generazione output stat_attori.tex
with open('stat_attori.tex', 'w', encoding='utf-8') as out:
    # Top 6 battute
    out.write(r"""
\section*{Top 6 attori per numero di battute}
\begin{tabular}{lr}
\toprule
Attore & Battute \\
\midrule
""" )
    for a, s in lines_sorted[:6]:
        out.write(f"{actor_names_display[a]} & {s['lines']} \\\n")
    out.write(r"""
\bottomrule
\end{tabular}
""" )
    # Top 6 parole
    out.write(r"""
\section*{Top 6 attori per numero di parole recitate}
\begin{tabular}{lr}
\toprule
Attore & Parole \\
\midrule
""" )
    for a, s in words_sorted[:6]:
        out.write(f"{actor_names_display[a]} & {s['words']} \\\n")
    out.write(r"""
\bottomrule
\end{tabular}
""" )
    # Top 10 pièce
    out.write(r"""
\section*{Top 10 attori per numero di pièce recitate}
\begin{tabular}{lr}
\toprule
Attore & Pièce \\
\midrule
""" )
    for a, s in pieces_sorted[:10]:
        out.write(f"{actor_names_display[a]} & {len(s['pieces'])} \\\n")
    out.write(r"""
\bottomrule
\end{tabular}
""" )
    # Tabelle per pièce
    for t, st in piece_stats.items():
        out.write("""
\section*{""" + t + r"""}
\begin{tabular}{lr}
\toprule
Statistiche & Valore \\
\midrule
Attore con più battute & """
                  + actor_names_display.get(st['most_lines_actor'], st['most_lines_actor']) + r""" \\
""" + 
                  "Attore con più parole & """ + actor_names_display.get(st['most_words_actor'], st['most_words_actor']) + r""" \\
""" + 
                  "Numero totale di battute & """ + str(st['lines']) + r""" \\
""" + 
                  "Numero totale di parole & """ + str(st['words']) + r""" \\
\bottomrule
\end{tabular}
""")

print("[✓] File 'stat_attori.tex' generato con successo.")

