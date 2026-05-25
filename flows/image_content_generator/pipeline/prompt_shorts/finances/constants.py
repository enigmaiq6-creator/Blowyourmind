# flake8: noqa: E501
AUDIO_PROMPT: str = "{audio_text}"

# --- NUEVA SERIE: ENIGMAIQ - CÓDIGOS DE RIQUEZA ---
IDEA_PROMPT_MINDSET: str = """# 🧠 GENERADOR DE IDEAS — SERIE: ENIGMAIQ (CÓDIGOS DE RIQUEZA)
**Objetivo:** Generar una lección de finanzas brutales, hábitos de riqueza o críticas a la mentalidad de pobreza.

**DIRECTIVA DE VARIEDAD INFINITA:**
Explora territorios psicológicos y prácticos sin repetir conceptos:
- **Hábitos Invisibles:** Gastos hormiga, inflación del estilo de vida, gratificación instantánea.
- **Disciplina de Hierro:** Madrugar, lectura, ahorro forzado, el "no" como superpoder.
- **Realidad Brutal:** Por qué los pobres siguen pobres, la trampa de la clase media, la mentira de los títulos.
- **Psicología del Dinero:** Miedo a invertir, envidia al éxito, mentalidad de escasez vs abundancia.
- **Sistemas de Riqueza:** Interés compuesto, activos vs pasivos, libertad vs seguridad.

**Reglas:**
- Título: Debe ser provocador y directo (sin números de parte).
- Tono: Crudo, directo, realista y premium.
- No repitas el mismo ángulo bajo ninguna circunstancia.
"""

# --- NUEVO MOTOR DE IMÁGENES SKETCH (ESTILO INFOGRAFÍA ENIGMAIQ) ---
IMAGE_INTERACTION_PROMPT: str = """# 🧩 GENERADOR DE INFOGRAFÍAS — ESTILO SKETCH (PEN & INK)
**OBJETIVO:** Generar un dibujo a tinta que compare dos situaciones financieras con etiquetas en ESPAÑOL.

**ESTILO VISUAL OBLIGATORIO (ENIGMAIQ):** 
- **Estilo**: Detailed hand-drawn pen and ink sketch on warm cream paper. 
- **Técnica**: Thick clean black lines, cross-hatching shadows, minimalist style, high contrast.
- **Contenido**: A split-screen comparison: on the left, [SITUACIÓN 1]; on the right, [SITUACIÓN 2].
- **Texto en Imagen**: Usa etiquetas simples en ESPAÑOL (ej: "Pobre" vs "Rico", "Error" vs "Acierto", "Mentalidad de Escasez" vs "Abundancia").
- **Personaje**: Expressive cartoon stickman, New Yorker cartoon aesthetic.
- **NO USAR**: Realistic photos, 3D, gradients, cinematic lighting.

**FORMATO DE RESPUESTA OBLIGATORIO (JSON):**
{
  "title": "Título corto y potente",
  "hook": "Gancho para detener el scroll",
  "idea_visual": "Comparación: Hábito pobre vs Hábito rico",
  "image_prompt": "Detailed hand-drawn pen and ink sketch on warm cream paper. A split-screen comparison with SPANISH LABELS. Left: [SITUACIÓN 1 con etiqueta 'Pobre']. Right: [SITUACIÓN 2 con etiqueta 'Rico']. Thick clean black lines, cross-hatching shadows, minimalist style, high contrast, clean white and black, emerald green highlights for money elements. No realistic photos, no 3D. New Yorker cartoon aesthetic.",
  "caption": "Pregunta cruda para Facebook.",
  "objetivo_psicologico": "Contraste"
}
"""

# Alias de compatibilidad
IDEA_PROMPT_ESTRATEGIA: str = IDEA_PROMPT_MINDSET
IDEA_PROMPT_HUSTLE: str = IDEA_PROMPT_MINDSET
SCRIPT_PROMPT: str = """# 📝 GUIONISTA MAESTRO — ESTRATEGIA DE RETENCIÓN 2026
**Objetivo:** Crear un video de 60 segundos con retención del 90% y comentarios masivos.

**ESTRATEGIA MAESTRA (OBLIGATORIA):**
1. **El Gancho (0-3s):** Debe ser una frase DISRUPTIVA que use una palabra clave del nicho inmediatamente. Ej: "El Biohacking es mentira si no haces esto...".
2. **Estilo Lo-Fi:** Las descripciones de imagen deben pedir un estilo "Hand-drawn sketch" o "Authentic iPhone photo", nada de renders perfectos.
3. **El Nudo (Explicación):** Datos fríos, lógica aplastante. No uses relleno.
4. **Cebo de Comentarios (Comment Bait):** Al final, NO pidas un like. Haz una pregunta que obligue a escribir más de 5 palabras.

**SEGURIDAD & CUMPLIMIENTO (CRÍTICO):**
- **NO des consejos médicos específicos** (ej: "toma X mg de tal suplemento").
- **NO des consejos financieros específicos** (ej: "compra la acción X").
- Mantén un tono **EDUCATIVO y FILOSÓFICO**.
- El contenido debe ser interpretado como entretenimiento e información general.

**Estructura de 4 Escenas:**
- Escena 1: HOOK visual y verbal potente.
- Escena 2: El error común que comete el 99%.
- Escena 3: La solución "Elite" (secreto del nicho).
- Escena 4: Pregunta de interacción + "Síguenos en EnigmaIQ".

**Reglas de Imagen (image_prompt en inglés):**
- Fondo crema, Stickman blanco minimalista. Estilo "Authentic hand-drawn ink sketch".
- Usa verde esmeralda solo para enfatizar dinero o éxito.
"""
