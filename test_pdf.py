import pdfplumber
import re

def test_full_parse():
    """Simulates the exact logic from alumnos_service.importar_alumnos_desde_pdf"""
    with pdfplumber.open('docs/alumnos.pdf') as pdf:
        current_nrc = None
        all_students = []
        
        for p_idx, pagina in enumerate(pdf.pages):
            text = pagina.extract_text()
            if not text:
                continue
            
            nrc_match = re.search(r'NRC:\s*(\d+)', text)
            if nrc_match:
                current_nrc = nrc_match.group(1)
            
            nrc_to_use = current_nrc if current_nrc else "UNKNOWN"
            
            lines = text.split('\n')
            last_student = None
            
            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue
                    
                match = re.search(r'^(\d+)\s+(.*?)\s+(\d{9})\s+\*\*Inscrito por Web\*\*\s+(.+?)\s+([\d\.]+)', line_str)
                if match:
                    nombre = match.group(2).strip()
                    matricula = match.group(3).strip()
                    
                    student = {"nombre": nombre, "matricula": matricula, "nrc": nrc_to_use}
                    all_students.append(student)
                    last_student = student
                elif last_student:
                    # Posible continuación del nombre
                    if not re.match(r'^\d+', line_str) and 'Clase' not in line_str and 'Página' not in line_str and 'Regresar' not in line_str and '©' not in line_str and 'VERSIÓN' not in line_str:
                        if re.match(r'^[A-Z\s\.,]+$', line_str):
                            last_student["nombre"] += " " + line_str
        
        print(f"NRC: {current_nrc}")
        print(f"Total students parsed: {len(all_students)}")
        print("---")
        for s in all_students:
            print(f"  {s['matricula']} | {s['nombre']} | NRC: {s['nrc']}")

test_full_parse()
