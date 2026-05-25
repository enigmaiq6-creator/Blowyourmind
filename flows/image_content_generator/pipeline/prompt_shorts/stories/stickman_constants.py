from typing import ClassVar

IDEA_PROMPT_STICKMAN = """
ROL: Eres un guionista experto en contenido de DESARROLLO PERSONAL de alto impacto. Tu misión es generar guiones cortos (aprox. 60-80 palabras) que sigan ESTRICTAMENTE la estructura de "Estoicismo Práctico" del siguiente ejemplo:

EJEMPLO DE ESENCIA (NO COPIAR LITERALMENTE):
"Comprendí que mis palabras son semillas de poder y que la mayoría de la gente las desperdicia sembrando maleza en campos ajenos.
Cada vez que te quejas por lo que no tienes o te unes al chisme para encajar, estás envenenando tu propia tierra.
Aprende a ser ahorrativo con tu voz. No todo pensamiento debe ser dicho ni toda discusión necesita tu opinión.
Elegir lo que dices con precisión es el primer paso para manifestar la realidad que quieres vivir."

ESTRUCTURA OBLIGATORIA (PLANTILLA):
Escena 1 (Metáfora): Comprendí que mi [Recurso del Tema] es [Símbolo Visual] y cómo el mundo lo desperdicia.
Escena 2 (El Error): Describe el fallo cotidiano del espectador y su consecuencia usando la metáfora.
Escena 3 (El Cambio): Consejo directo que empiece SIEMPRE con "Aprende a ser...".
Escena 4 (La Sentencia): Conecta la acción con el resultado final de vida.

🚨 IMPORTANTE: Crea una METÁFORA ÚNICA basada en el tema '{selected_area}'. NO uses semillas ni palabras si el tema es otro.

REGLAS DE ESTILO:
- Tono: Solemne, sabio y empoderador.
- Vocabulario: Riqueza, santuario, moneda, veneno, arquitecto, guardián, desperdicio, semillas.
- TEMA CENTRAL OBLIGATORIO: {selected_area}

DIRECCIÓN DE ARTE:
Estilo "Preguntas y Trivias": Ilustración digital atmosférica, colores vibrantes (azul/naranja), personaje stickman expresivo con rim lighting.
Simbología: Incluye elementos que brillan (llaves, fuego, hilos de luz).

INSTRUCCIONES DE MOVIMIENTO:
Define V1, V2, V3, V4 para animar las escenas.

REGLA DE EVITACIÓN:
{avoid_msg}

IMPORTANTE: Responde ÚNICAMENTE con el JSON siguiendo este formato:
{{
  "title": "Título del Video",
  "hook": "Frase de gancho inicial (MÁX 10 palabras)",
  "selected_theme": "{selected_area}",
  "selected_symbol": "Símbolo visual principal usado",
  "scenes": [
    {{
      "scene_number": 1,
      "narration": "Texto completo de la Escena 1",
      "image_prompt": "Prompt de imagen detallado para la Escena 1",
      "movement_instruction": "V1: Instrucción de movimiento"
    }},
    ... (total 4 escenas)
  ]
}}
"""

AUDIO_PROMPT_STICKMAN = """
Usa un tono ESTOICO, SOLEMNE y PODEROSO. 
Lee con calma, dándole peso a palabras como "riqueza", "veneno" o "arquitecto".
Pausas marcadas entre cada párrafo para que el mensaje penetre.

TEXTO A NARRAR:
{audio_text}
"""
