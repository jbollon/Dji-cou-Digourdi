import os
import re
from collections import defaultdict

# Lista dei file TeX
tex_files = [
    "2009.tex", "2010.tex", "2011.tex", "2012.tex", "2013.tex",
    "2014.tex", "2015.tex", "2016.tex", "2018.tex", "2019.tex"
]

time_p = [36, 42, 50, 44, 54, 34, 74, 68, 59, 61]

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
             'eugn', 'tan', 'tcheutte', 'iaou', 'qui', 'tchica', 'mimo', 'deun',
             'noutro', 'naaa', "wow", 'praou', 'seutte', 'perqué', 'tcheut',
             'dou', 'trèi', 'ouette', 'voualà', 'pouèi',
             'cou', 'ren', 'vouè',
             'bièn', 'bon', 'amoddo',
             'hélène', 'twitter', 'paolo', 'giulio', 'selmo', 'gène', 'tanteun', 'vilma', 'bruno',
             'tsarvensoù', 'pollein', 'digourdì', 'touéno', 'feleunna', 'marie', 'rémy',
             'hermann', 'sandrino', 'alice',
             #'djeusto', 'dzen', 'dzenta', ### adj
             'oueu', 'todzor', 'aprì', 'inque',
             'ouè',
             'sen', 'son', 'ouèide', 'ouite', 'nen', 'ayè', 'ouyavade', 'soplé',
             'deu', 'veun', 'vou', 'fièn', 'fiade', 'beutta', 'fenì', 'vère', 'payo',
             'bèye', 'gagnà', 'comprèi', 'itedjà', 'veure', 'lavave', 'vouillade',
             #
             'mersì', 'bondzor', 'bonsouar'
             ]

eff_tot = 0 ; video_tot = 0 ; mus_tot = 0

# Parsing dei file
for kk, filename in enumerate(tex_files):
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
    
    sounds = re.findall(r"\\sound{.*?}{.*?}", content)
    sounds_false = re.findall(r"\\sound{.*?}{.*?}\[.*?\]", content)
    
    effets = re.findall(r"\\effet{.*?}{.*?}", content)
    effets_false = re.findall(r"\\effet{.*?}{.*?}\[.*?\]", content)
    
    videos = re.findall(r"\\StartVideo{.*?}", content)
    videos = [x.count(',')+1 for x in videos]
    
    if filename != '2009.tex':
        words_set_ordered = sorted(words_set.items(), key=lambda x: x[1], reverse=True)

    # Conta battute e parole
    for macro, actor in character_map.items():
        speak_pat = re.compile(r'^\\' + re.escape(macro) + r'speaks\b(.*)$', re.MULTILINE)
        for sp in speak_pat.findall(content_piece):
            piece_lines += 1
            actor_stats[actor]['lines'] += 1
            actor_stats[actor]['pieces'].add(title)
            actor_lines[actor] += 1
            #escludo tutto il testo dentro eventuali comandi, i.e. \direct{}
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
    n_eff = len(effets) - len(effets_false)
    n_mus = len(sounds) - len(sounds_false)
    
    piece_stats[title] = {'lines': piece_lines, 'words': piece_words,
                          'set_words': words_piece,
                          'mostwp': mostwp,
                          'time': time_p[kk],
                          'n_sounds': n_mus,
                          'n_effets': n_eff,
                          'n_video': sum(videos),
                          'n_actors': len(actor_words.keys()),
                          'most_lines_actor': [mostl, actor_lines[mostl]],
                          'most_words_actor': [mostw, actor_words[mostw]]}
    
    print(title)
    eff_tot += n_eff ; video_tot += sum(videos) ; mus_tot += n_mus
     

# Ordinamento
'''
words_at_least1 = dict()
checked_word = []
for tit in piece_stats.keys():
    set_words = sorted(piece_stats[tit]['set_words'].items(), key=lambda x: x[1], reverse=True) if piece_stats[tit]['set_words'] else '—'
    
    for w in set_words:
        k = w[0] ; v = w[1]
        if k not in checked_word:
            checked_word.append(k)
            check = 0
            for tit_j in piece_stats.keys():
                if tit != tit_j:
                    if k in piece_stats[tit_j]['set_words'].keys():
                        check += 1
                        v = min(v, piece_stats[tit_j]['set_words'][k])
                    else:
                        break
            if check >= 9:     
                words_at_least1[k] = v
        
    '''    


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
        actor_stats[actor]['top_w'] = ""
        
    actor_stats[actor]['n_pièce'] = len(actor_stats[actor]['pieces'])

n_actors = len(actor_stats.keys())
actor_stats = sorted(actor_stats.items(), key=lambda x: x[0].split(' ')[1]+' '+x[0].split(' ')[0], reverse=False)



# Generazione output stat_attori.tex
with open('Appendice/stat_attori.tex', 'w', encoding='utf-8') as out:
    # Totaloni
    tot_w = sum(words_set_all.values())
    tot_lines = sum([piece_stats[t]['lines'] for t in piece_stats.keys()])
    out.write(r"""
\vfill
\begin{table}[h]
\centering
\caption{Les numéros de Dji cou Digourdì.}
\begin{tabular}{lr}
    \toprule""")
    out.write('\nParoles & ' + f"{tot_w}" + r' \\')
    out.write('\nParoles non répétés & ' + f"{len(words_set_all.keys())}" + r' \\')

    #out.write('\nMots & ' + f"{sum(words_set.values())}" + r' \\')
    #out.write('\nMots non répétés & ' + f"{len(words_set.keys())}" + r' \\')
    
    out.write("\nRépliques & " + f"{tot_lines}" + r' \\')
    out.write('\nActeurs & ' + f"{n_actors}" + r' \\')
    out.write('\nVidéos & ' + f"{video_tot}" + r' \\')
    out.write('\nEffets sonores & ' + f"{eff_tot}" + r' \\')
    out.write('\nMusiques & ' + f"{mus_tot}" + r' \\')
    out.write(r"""
\bottomrule
\end{tabular}%
\end{table}
\vfill""")

    # Top 10  parole
    out.write(r"""
\newpage
\vfill
\begin{table}[h]
\centering
\caption{Les 10 mots les plus prononcés.}
\begin{tabular}{lr}
    \toprule
""")
    for a, s in words_set_ordered[:11]:
        out.write('\n\multicolumn{1}{l}{' + f"{up_first(a)}" + '} &' + f"{s}" + r'\\')
    out.write(r"""
\bottomrule
\end{tabular}%
\end{table}
\vfill""")

    # Tous le acteurs
    out.write(r"""
\newpage
\scriptsize
\begin{longtable}{llrrr}
\caption{\small Ce tableau présente tous les acteurs de Dji Cou Digourdì, accompagnés par leurs nombre de participation aux pièces, répliques, paroles et leurs trois mots les plus fréquemment prononcés. L'absence de trois mots s'explique par l'impossibilité d'identifier les trois plus fréquents.}\\
\toprule
\textbf{Acteurs} & \textbf{Top 3 mots} & \textbf{Pièces} & \textbf{Répliques} & \textbf{Paroles} \\
    \midrule""")
    x = 0
    for a, s in actor_stats:
        x += s['words']
        name = f"{actor_names_display[a]}" + ' &'

        out.write('\n' + name + f"{s['top_w']}" + f" & {s['n_pièce']}" + f" & {s['lines']}" + f" & {s['words']}" + r'\\')
    out.write(r"""
\bottomrule
\end{longtable}""")
    #print(x)
# Top 6 battute
    out.write(r"""
\begin{table}[]
\centering
\caption{Les trois acteurs comptant le plus de répliques.}
\begin{tabular}{l|r}
\toprule
\multicolumn{1}{l}{\textbf{Acteur}} & \textbf{Répliques} \\
""")
    for a, s in lines_sorted[:4]:
        out.write('\n\multicolumn{1}{l}{' + f"{actor_names_display_std[a]}" + '} &' + f"{s['lines']}" + r'\\')
    out.write(r"""
\bottomrule
\end{tabular}%
\end{table}
\newpage""")
    
    # Top 6 parole
    out.write(r"""
\begin{table}[]
\centering
\caption{Les trois acteurs comptant le plus de mots prononcés.}
\begin{tabular}{l|r}
    \toprule
\multicolumn{1}{l}{\textbf{Acteurs}} & \textbf{Paroles} \\
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
\caption{Les trois acteurs les plus présents.}
\begin{tabular}{lr}
    \toprule
\multicolumn{1}{l}{\textbf{Acteur}} & \textbf{Pièces} \\
    \midrule""")
    for a, s in pieces_sorted[:4]:
        out.write('\n\multicolumn{1}{l}{' + f"{actor_names_display[a]}" + '} &' + f"{len(s['pieces'])}" + r'\\')
    out.write(r"""
\bottomrule
\end{tabular}%
\end{table}
\newpage""")

    if True:
        # Tab per pièce
        for t, st in piece_stats.items():
            
            x = st['mostwp'][::-1]
            mostwp = f"{up_first(x[0][0])}, {up_first(x[1][0])}, {up_first(x[2][0])}"
            
            out.write(r"""
    \begin{table}[]
    \centering
    \caption{}
    \begin{tabular}{lr}""")
            out.write(r"""\toprule""")
            out.write('\multicolumn{2}{c}{' + f"{t}" + '} \\\\')
            out.write(r"""\midrule""")
            
            out.write("\n\multicolumn{1}{l}{Durée (min)}&" + f"{st['time']}" + r'\\')
            out.write("\n\multicolumn{1}{l}{Nombre d'acteurs}&" + f"{st['n_actors']}" + r'\\')
            
            out.write("\n\multicolumn{1}{l}{Nombre de vidéos}&" + f"{st['n_video']}" + r'\\')
            out.write("\n\multicolumn{1}{l}{Nombre de musiques}&" + f"{st['n_sounds']}" + r'\\')
            out.write("\n\multicolumn{1}{l}{Nombre d'effets sonores}&" + f"{st['n_effets']}" + r'\\')
            
            out.write('\n\multicolumn{1}{l}{Nombre de paroles}&' + f"{st['words']}" + r'\\')
            out.write('\n\multicolumn{1}{l}{Nombre de répliques}&' + f"{st['lines']}" + r'\\')
            
            n = actor_names_display[st['most_words_actor'][0]]
            out.write('\n\multicolumn{1}{l}{Acteur avec le plus de paroles}&' + f"{n} ({st['most_words_actor'][1]})" + r'\\')
            
            n = actor_names_display[st['most_lines_actor'][0]]
            out.write('\n\multicolumn{1}{l}{Acteur avec le plus de répliques}&' + f"{n} ({st['most_lines_actor'][1]})" + r'\\')
            
            out.write('\n\multicolumn{1}{l}{Mots les plus prononcés}&' + f"{mostwp}" + r'\\')
        
            out.write(r"""
    \bottomrule
    \end{tabular}%
    \end{table}""")
    
    
    # Stat top/flop pièce
    longest = sorted(piece_stats.items(), key=lambda x: x[1]['time'], reverse=True)[0]
    longest = longest[0] + f" ({str(longest[1]['time'])})"
    
    shortest = sorted(piece_stats.items(), key=lambda x: x[1]['time'], reverse=True)[-1]
    shortest = shortest[0] + f" ({str(shortest[1]['time'])})"
    
    top_rep_min = sorted(piece_stats.items(), key=lambda x: x[1]['lines']/x[1]['time'], reverse=True)[0]
    top_rep_min = top_rep_min[0] + f" ({round(top_rep_min[1]['lines']/top_rep_min[1]['time'], 1)})"
    
    flop_rep_min = sorted(piece_stats.items(), key=lambda x: x[1]['lines']/x[1]['time'], reverse=True)[-1]
    flop_rep_min = flop_rep_min[0] + f" ({round(flop_rep_min[1]['lines']/flop_rep_min[1]['time'], 1)})"
    
    top_w_min = sorted(piece_stats.items(), key=lambda x: x[1]['words']/x[1]['time'], reverse=True)[0]
    top_w_min = top_w_min[0] + f" ({round(top_w_min[1]['words']/top_w_min[1]['time'], 1)})"
    
    flop_w_min = sorted(piece_stats.items(), key=lambda x: x[1]['words']/x[1]['time'], reverse=True)[-1]
    flop_w_min = flop_w_min[0] + f" ({round(flop_w_min[1]['words']/flop_w_min[1]['time'], 1)})"
    
    out.write(r"""
\begin{table}[h]
\centering
\caption{Résumé des pièces.}
\begin{tabular}{lr}
    \toprule""")
    out.write('\nLa plus longue (min) & ' + f"{longest}" + r' \\')
    out.write('\nLa plus courte (min) & ' + f"{shortest}" + r' \\')
    out.write('\nTop répliques/min & ' + f"{top_rep_min}" + r' \\')
    out.write('\nTop paroles/min & ' + f"{top_w_min}" + r' \\')
    out.write(r"""
\bottomrule
\end{tabular}%
\end{table}""")
         

print("[✓] File 'stat_attori.tex' generato con successo.")

