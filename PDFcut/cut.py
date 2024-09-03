import fitz  # PyMuPDF
import cv2
import numpy as np
from pathlib import Path
import re

def extract_gears_from_pdf(pdf_path, output_folder):
    # Crear carpeta de salida si no existe
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Abrir el PDF
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Obtener la imagen de la página
        pix = page.get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Binarizar la imagen
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filtrar por tamaño (ajustar según sea necesario)
            if 100 < w < 300 and 100 < h < 300:
                # Recortar la región de interés
                roi = img[y:y+h, x:x+w]
                
                # Buscar la referencia cerca del contorno
                ref_roi = binary[y+h:y+h+50, x:x+w]
                ref_text = pytesseract.image_to_string(ref_roi)
                
                # Extraer la referencia con una expresión regular
                match = re.search(r'[FP]\d+/R\d+', ref_text)
                if match:
                    filename = f"{match.group()}.jpg"
                    cv2.imwrite(f"{output_folder}/{filename}", roi)

if __name__ == "__main__":
    pdf_path = "ruta/al/catalogo.pdf"
    output_folder = "ruta/a/la/carpeta/de/salida"
    extract_gears_from_pdf(pdf_path, output_folder)