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
a_character = re.compile(
    r'\\Character\[[^\]]*\]'
    r'\{\s*[^}]+?\s*\}'
    r'\{\s*([^}]+?)\s*\}'
    r'\{[\s\S]*?\\nameF?\{\s*([^{}]+?(?:\{[^}]*\}[^{}]*)*)\s*\}[\s\S]*?\}',
    re.DOTALL
)
name_pattern = re.compile(r'\\nameF?\{([^\}]+)\}')
direct_pattern = re.compile(r'\\direct\{.*?\}')
title_pattern = re.compile(r'\\title\{([^\}]+)\}')

# Strutture dati per le statistiche
actor_stats = defaultdict(lambda: {"pieces": set(), "lines": 0, "words": 0, "dict_words":dict()})
actor_names_display = {}  # normalizzato -> display
actor_names_display_std = {}
piece_stats = {}

# set di parole
words_set = dict()
words_set_all = dict()
exclude_w = ['que', 'eun', 'eunna', 'can', 'avouì', 'euncó', 'ara', 'senque',
             'lèi', 'comme', 'comèn', 'adón', 'maque', 'seutta', 'seuilla',
             'fran', 'tcheu', 'dza', 'totte', 'pequé', 'sise', 'pamì', 'salla',
             'eugn', 'tan', 'tcheutte', 'iaou', 'qui', 'tchica', 'mimo',
             'noutro', 'naaa', "wow", 'praou', 'seutte', 'perqué', 'tcheut',
             'dou', 'trèi', 'ouette', 'voualà',
             'cou', 'ren', 'vouè',
             'bièn', 'bon',
             #'djeusto', 'dzen', 'dzenta', ### adj
             'oueu', 'todzor', 'aprì', 'inque',
             'ouè',
             'sen', 'son', 'ouèide', 'ouite', 'nen', 'ayè', 'ouyavade'
             #'deu', 'veun', 'vou', 'fièn', 'fiade'
             ]

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
    for macro, raw_name in a_character.findall(content):

        display_name = normalize_latex_accents(raw_name).strip()
        normalized = display_name.lower()
        character_map[macro] = normalized
        
        actor_names_display_std[normalized] = display_name
        display_name = ' '.join(display_name.split(' ')[1:]) + ' ' + display_name.split(' ')[0]
        actor_names_display[normalized] = display_name

    # Contatori per la pièce
    piece_lines = 0
    piece_words = 0
    actor_lines = defaultdict(int)
    actor_words = defaultdict(int)
    words_piece = dict()
    
    content_piece = re.sub(r'(?s)^.*?(\\act\[Acte I\])', r'\1', content)
    
    if filename != '2009.tex':
        words_set_ordered = sorted(words_set.items(), key=lambda x: x[1], reverse=True)
        
    print(filename)

    # Conta battute e parole
    for macro, actor in character_map.items():
        speak_pat = re.compile(r'^\\' + re.escape(macro) + r'speaks\b(.*)$', re.MULTILINE)
        for sp in speak_pat.findall(content_piece):
            piece_lines += 1
            actor_stats[actor]['lines'] += 1
            actor_stats[actor]['pieces'].add(title)
            actor_lines[actor] += 1
            
            sp = re.sub(r'\\[A-Za-z]+\{[^}]*\}|\\[A-Za-z]+', '', sp)
            
            words = re.findall(r'\b\w+\b', sp)
            for w in words:
                w = w.lower()
                
                if w in words_set_all.keys():
                    words_set_all[w] += 1
                else:
                    words_set_all[w] = 1
                
                if len(w) > 2 and w not in exclude_w:
                    
                    if w in words_set.keys():
                        words_set[w] += 1
                    else:
                        words_set[w] = 1
                        
                    if w in words_piece.keys():
                        words_piece[w] += 1
                    else:
                        words_piece[w] = 1
                        
                    if w in actor_stats[actor]['dict_words'].keys():
                        actor_stats[actor]['dict_words'][w] += 1
                    else:
                        actor_stats[actor]['dict_words'][w] = 1
            
            cnt = len(words)
            actor_stats[actor]['words'] += cnt
            actor_words[actor]  += cnt
            piece_words += cnt
        
        #if actor_lines[actor] > 0 :
         #   actor_stats[actor]['wl'] += round(actor_words[actor] / actor_lines[actor], 1)

    mostl = max(actor_lines.items(), key=lambda x: x[1])[0] if actor_lines else '—'
    mostw = max(actor_words.items(), key=lambda x: x[1])[0] if actor_words else '—'
    mostwp = sorted(words_piece.items(), key=lambda x: x[1])[-4:] if words_piece else '—'
    piece_stats[title] = {'lines': piece_lines, 'words': piece_words,
                          'mostwp': mostwp,
                          'n_actors': len(actor_words.keys()),
                          'most_lines_actor': [mostl, actor_lines[mostl]],
                          'most_words_actor': [mostw, actor_words[mostw]]}
     

# Ordinamento
#for k in actor_stats.keys():
#    actor_stats[k]['wl'] = round(actor_stats[k]['words'] / actor_stats[k]['lines'] * len(actor_stats[k]['pieces']), 1)
lines_sorted = sorted(actor_stats.items(), key=lambda x: x[1]['lines'], reverse=True)
words_sorted = sorted(actor_stats.items(), key=lambda x: x[1]['words'], reverse=True)
pieces_sorted = sorted(actor_stats.items(), key=lambda x: len(x[1]['pieces']), reverse=True)
#wl_sorted = sorted(actor_stats.items(), key=lambda x: x[1]['wl'], reverse=True)
words_set_ordered = sorted(words_set.items(), key=lambda x: x[1], reverse=True)

def up_first(text):
    return text.upper()[0] + text[1:]

agg_actors = dict()
for actor in actor_stats.keys():
    top_w = sorted(actor_stats[actor]['dict_words'].items(), key=lambda x: x[1], reverse=True)
    
    if top_w[2][1] != top_w[3][1]:
        actor_stats[actor]['top_w'] = f"{up_first(top_w[0][0])}, {up_first(top_w[1][0])}, {up_first(top_w[2][0])}"
    elif top_w[1][1] != top_w[2][1]:
        actor_stats[actor]['top_w'] = f"{up_first(top_w[0][0])}, {up_first(top_w[1][0])}"
    elif top_w[0][1] != top_w[1][1]:
        actor_stats[actor]['top_w'] = f"{up_first(top_w[0][0])}"
    else:
        actor_stats[actor]['top_w'] = f""
        
    actor_stats[actor]['n_pièce'] = len(actor_stats[actor]['pieces'])

actor_stats = sorted(actor_stats.items(), key=lambda x: x[0].split(' ')[1]+' '+x[0].split(' ')[0], reverse=False)

# Generazione output stat_attori.tex
with open('stat_attori.tex', 'w', encoding='utf-8') as out:
    # Totaloni
    tot = sum(words_set_all.values())
    out.write(r"""
\begin{table}[]
\centering
\begin{tabular}{lr}
\multicolumn{2}{c}{Tot} \\
    \toprule""")
    out.write('\nTot parole & ' + f"{tot}" + r' \\')
    out.write(r"""
\bottomrule
\end{tabular}%
\end{table}""")

    # Top 10  parole
    out.write(r"""
\begin{table}[]
\centering
\begin{tabular}{lr}
\multicolumn{2}{c}{Les 10 mots les plus dits} \\
    \toprule
\multicolumn{1}{l}{\textbf{Mot}} & \textbf{N} \\
    \midrule""")
    for a, s in words_set_ordered[:11]:
        out.write('\n\multicolumn{1}{l}{' + f"{up_first(a)}" + '} &' + f"{s}" + r'\\')
    out.write(r"""
\bottomrule
\end{tabular}%
\end{table}""")

    # Tous le acteurs
    out.write(r"""
\newpage
\scriptsize
\begin{longtable}{llrrr}
\caption{Tous les acteurs}\\
\toprule
\textbf{Acteur} & \textbf{Top 3 mots} & \textbf{Pièce} & \textbf{Lignes} & \textbf{Mots} \\
    \hline""")
    for a, s in actor_stats:
        name = f"{actor_names_display[a]}" + ' &'
        out.write('\n' + name + f"{s['top_w']}" + f" & {s['n_pièce']}" + f" & {s['lines']}" + f" & {s['words']}" + r'\\')
    out.write(r"""
\bottomrule
\end{longtable}""")
  
# Top 6 battute
    out.write(r"""
\begin{table}[]
\centering
\caption{Les 3 acteurs avec plus de lignes}
\begin{tabular}{l|r}
\toprule
\multicolumn{1}{l}{\textbf{Acteur}} & \textbf{Lignes} \\
\midrule
""")
    for a, s in lines_sorted[:4]:
        out.write('\n\multicolumn{1}{l}{' + f"{actor_names_display_std[a]}" + '} &' + f"{s['lines']}" + r'\\')
    out.write(r"""
\bottomrule
\end{tabular}%
\end{table}""")
    
    # Top 6 parole
    out.write(r"""
\begin{table}[]
\centering
\caption{Les 3 acteurs avec plus de mots}
\begin{tabular}{l|r}
    \toprule
\multicolumn{1}{l}{\textbf{Acteurs}} & \textbf{Mots} \\
    \midrule""")
    for a, s in words_sorted[:4]:
        out.write('\n\multicolumn{1}{l}{' + f"{actor_names_display_std[a]}" + '} &' + f"{s['words']}" + r'\\')
    out.write(r"""
\bottomrule
\end{tabular}%
\end{table}""")
    
    # Top 6 presenze
    out.write(r"""
\begin{table}[]
\centering
\caption{Les 3 acteurs plus présents}
\begin{tabular}{lr}
    \toprule
\multicolumn{1}{l}{\textbf{Acteur}} & \textbf{Pièce} \\
    \midrule""")
    for a, s in pieces_sorted[:4]:
        out.write('\n\multicolumn{1}{l}{' + f"{actor_names_display[a]}" + '} &' + f"{len(s['pieces'])}" + r'\\')
    out.write(r"""
\bottomrule
\end{tabular}%
\end{table}""")

    if True:
        # Tab per pièce
        for t, st in piece_stats.items():
            
            x = st['mostwp'][::-1]
            mostwp = f"{up_first(x[0][0])}, {up_first(x[1][0])}, {up_first(x[2][0])}"
            
            out.write(r"""
    \begin{table}[]
    \centering
    %\caption{desc...}
    \begin{tabular}{lr}""")
            out.write(r"""\toprule""")
            out.write('\multicolumn{2}{c}{' + f"{t}" + '} \\\\')
            out.write(r"""\midrule""")
            
            out.write("\n\multicolumn{1}{l}{Nombre d'acteur}&" + f"{st['n_actors']}" + r'\\')
            
            out.write('\n\multicolumn{1}{l}{Numero totale di parole}&' + f"{st['words']}" + r'\\')
            out.write('\n\multicolumn{1}{l}{Numero totale di battute}&' + f"{st['lines']}" + r'\\')
            
            n = actor_names_display[st['most_words_actor'][0]]
            out.write('\n\multicolumn{1}{l}{Attore con più parole}&' + f"{n} ({st['most_words_actor'][1]})" + r'\\')
            
            n = actor_names_display[st['most_lines_actor'][0]]
            out.write('\n\multicolumn{1}{l}{Attore con più battute}&' + f"{n} ({st['most_lines_actor'][1]})" + r'\\')
            
            out.write('\n\multicolumn{1}{l}{Parole più usate}&' + f"{mostwp}" + r'\\')
        
            out.write(r"""
    \bottomrule
    \end{tabular}%
    \end{table}""")
         

print("[✓] File 'stat_attori.tex' generato con successo.")

