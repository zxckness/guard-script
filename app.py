from flask import Flask, render_template, request
import random
import os

app = Flask(__name__)

class OrganizadorGuardia:
    def __init__(self, soldados, guardias_por_dia):
        self.soldados = soldados
        self.guardias_por_dia = guardias_por_dia
        random.shuffle(self.soldados)
        
        self.estado_ayer = {
            'GUARDIA': self.soldados[:guardias_por_dia],
            'PASE': self.soldados[guardias_por_dia:guardias_por_dia*2],
            'RETEN_1': self.soldados[guardias_por_dia*2:],
            'RETEN_2': []
        }
        
    def avanzar_dia(self, dia_nombre):
        hoy = {'GUARDIA': [], 'PASE': [], 'RETEN_1': [], 'RETEN_2': []}
        
        # 1. Los que hicieron Guardia y los "cuarto bate" pasan a Pase
        hoy['PASE'].extend(self.estado_ayer['GUARDIA'])
        hoy['PASE'].extend(self.estado_ayer['RETEN_2'])
        
        # 2. Los que estaban de Pase, vuelven a entrar al Retén
        hoy['RETEN_1'].extend(self.estado_ayer['PASE'])
        
        # --- LÓGICA DE ROTACIÓN PARA EL CUARTO BATE ---
        # Obtenemos la lista actual de disponibles para guardia
        candidatos_guardia = self.estado_ayer['RETEN_1']
        
        # SI hay más de un soldado, rotamos la lista: 
        # El primero pasa a ser el último. 
        # Esto hace que el "cuarto bate" de ayer no sea el mismo siempre.
        if len(candidatos_guardia) > 1:
            candidatos_guardia = candidatos_guardia[1:] + [candidatos_guardia[0]]
            
        # 3. Asignación según la nueva lista rotada
        if len(candidatos_guardia) >= self.guardias_por_dia:
            hoy['GUARDIA'] = candidatos_guardia[:self.guardias_por_dia]
            hoy['RETEN_2'] = candidatos_guardia[self.guardias_por_dia:]
        else:
            hoy['GUARDIA'] = candidatos_guardia
            
        self.estado_ayer = hoy
        
        return {
            'Día': dia_nombre,
            'Guardia': ", ".join(hoy['GUARDIA']) if hoy['GUARDIA'] else "Ninguno",
            'Retén': ", ".join(hoy['RETEN_1'] + hoy['RETEN_2']) if (hoy['RETEN_1'] + hoy['RETEN_2']) else "Ninguno",
            'Pase': ", ".join(hoy['PASE']) if hoy['PASE'] else "Ninguno"
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    calendario = None
    if request.method == 'POST':
        nombres_raw = request.form.get('soldados')
        guardias_por_dia = int(request.form.get('guardias_por_dia', 3))
        
        lista_soldados = [nombre.strip() for nombre in nombres_raw.split('\n') if nombre.strip()]
        
        if lista_soldados and guardias_por_dia > 0:
            # Usamos una copia para no alterar la original si quisieras extender el calendario
            organizador = OrganizadorGuardia(lista_soldados, guardias_por_dia)
            dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            calendario = []
            
            for dia in dias_semana:
                calendario.append(organizador.avanzar_dia(dia))
                
    return render_template('index.html', calendario=calendario)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
