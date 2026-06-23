import sys
import os
from pypdf import PdfReader, PdfWriter

def ritaglia_margini_pdf(input_path, output_path, mm_da_togliere=3.0):
    """
    Ritaglio di 3mm da tutti i lati di un PDF modificando la CropBox.
    """
    # Conversione mm in punti PDF (1 pollice = 25.4 mm = 72 punti)
    punti_per_mm = 72 / 25.4
    offset = mm_da_togliere * punti_per_mm

    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()

        for pagina in reader.pages:
            # Prende la CropBox attuale (l'area visibile)
            box = pagina.cropbox

            # Calcola i nuovi margini restringendo il rettangolo
            nuovo_lower_left_x = box.lower_left[0] + offset
            nuovo_lower_left_y = box.lower_left[1] + offset
            nuovo_upper_right_x = box.upper_right[0] - offset
            nuovo_upper_right_y = box.upper_right[1] - offset

            # Applica i nuovi limiti
            pagina.cropbox.lower_left = (nuovo_lower_left_x, nuovo_lower_left_y)
            pagina.cropbox.upper_right = (nuovo_upper_right_x, nuovo_upper_right_y)
            
            writer.add_page(pagina)

        # Salva il file risultante
        with open(output_path, "wb") as fp:
            writer.write(fp)
        
        print(f"Successo! File salvato come: {output_path}")

    except Exception as e:
        print(f"Errore durante l'elaborazione: {e}")

if __name__ == "__main__":
    # Controllo che siano stati passati i due argomenti necessari
    if len(sys.argv) != 3:
        print("Utilizzo corretto: python main.py <file_input.pdf> <file_output.pdf>")
        sys.exit(1)

    file_in = sys.argv[1]
    file_out = sys.argv[2]

    # Verifica se il file di input esiste
    if not os.path.exists(file_in):
        print(f"Errore: Il file '{file_in}' non esiste.")
        sys.exit(1)

    ritaglia_margini_pdf(file_in, file_out)
