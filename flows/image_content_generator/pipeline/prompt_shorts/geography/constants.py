# Prompt constants for Geography/History Reels

IDEA_PROMPT_GEOGRAPHY = """
Genera una idea altamente viral para un video corto sobre "Curiosidades Geográficas y Climáticas de Latinoamérica".
El tema debe ser **EXTREMADAMENTE ASOMBROSO Y FASCINANTE**, explicando cómo la geografía de un lugar (montañas, costas, ríos, desiertos) define su clima, su vida o su historia.
Ejemplos ideales:
- "¿Por qué la costa del Pacífico colombiano es uno de los lugares más lluviosos del planeta?"
- "¿Cómo la cordillera de los Andes actúa como un muro gigante que divide climas y biodiversidad?"
- "El misterio de los ríos voladores de la Amazonía."
- "¿Por qué la geografía de Colombia la convierte en una potencia mundial de agua y biodiversidad?"

El video debe tener un guion que explique todo el concepto de principio a fin, con un gancho brutal de inicio, desarrollo y una **CONCLUSIÓN CERRADA** y satisfactoria.
Debe estar pensado para un video fluido, de ritmo rápido, compuesto por **6 a 8 escenas cortas** para que visualmente nunca se sienta estancado.
La narración completa de TODAS las escenas sumadas NO DEBE SUPERAR LAS 120 PALABRAS, para garantizar que el video dure menos de 60 segundos.

**ESTILO VISUAL DE IMAGEN DE RESPALDO (si se requiere):**
Aplica un estilo cinematográfico detallado: "{visual_style}"
"""

AUDIO_PROMPT_GEOGRAPHY = """
Usa un tono narrativo formal, profesional, extremadamente intrigante, dramático e informativo. Como el narrador de un documental premium de geografía e historia de gran presupuesto (estilo Vox o RealLifeLore).

TEXTO A NARRAR:
{audio_text}
"""

SCRIPT_PROMPT_GEOGRAPHY = """
Basándote en la IDEA de geografía e historia proporcionada, escribe un guion de video estructurado para un Reel de máximo 50 segundos.
Divide el video en **6 a 8 escenas cortas** con alta densidad visual y dinamismo.

Para cada escena debes definir:
1. `scene_number`: Número secuencial (1 a N).
2. `visual_type`: Escoge `"map_3d"` (por defecto para mostrar mapas satelitales 3D, relieves, barreras de viento, etc.), o `"stock_video"` (para clips de selvas, playas, lluvia, gente), o `"ai_image"` (para recrear escenas históricas, cavernícolas o esquemas muy específicos de corte transversal de la Tierra).
3. `pexels_query`: Si elegiste `"stock_video"`, escribe 1 a 3 palabras clave EN INGLÉS (ej. 'amazon jungle drone', 'heavy rain pacific', 'andes mountains'). Deja vacío en caso contrario.
4. `image_prompt`: La descripción detallada EN INGLÉS del estilo visual que debe tener la imagen de respaldo (siempre obligatoria).
5. `narration`: Lo que dirá el locutor de forma fluida e intrigante en español (LATAM).
6. `camera`: Configuración de la cámara del mapa satelital 3D (aunque la escena sea stock_video, define esto para pre-ubicar la posición geográfica relativa de la escena):
   - `latitude`: Latitud exacta del lugar (ej. 4.570868 para Colombia, -15.783333 para Brasil).
   - `longitude`: Longitud exacta del lugar (ej. -74.297333 para Colombia, -47.916667 para Brasil).
   - `zoom`: Nivel de zoom del mapa (valores decimales entre 3.0 para continente y 12.0 para ciudades/cordilleras).
   - `pitch`: Inclinación de la cámara (valores entre 30 y 60 grados para dar un look 2.5D/3D).
   - `bearing`: Dirección de la cámara en grados (entre -180 y 180 para rotar el mapa).
7. `highlight_region`: Nombre de la región, país o accidente geográfico que se debe colorear y resaltar en el mapa (ej. 'Colombia', 'Brazil', 'Andes Mountains', 'Pacific Coast', 'Amazon Basin', o 'none').
8. `arrow_direction`: Describe brevemente el flujo de una flecha animada sobre el mapa si aplica (ej. 'from: Pacific Ocean, to: Andes Mountains' para mostrar el viento bloqueado, o 'from: Amazon River, to: Atlantic Ocean', o 'none').
9. `floating_label`: Una etiqueta flotante con datos de impacto en mayúsculas (ej: '52.32 MILLONES', '3 CORDILLERAS', '8,000 MM DE LLUVIA', o 'none').
10. `sfx`: Efecto de sonido ambiental o de impacto para esta escena (escoge entre: 'jungle_ambient', 'rain_and_thunder', 'heavy_wind', 'digital_swoosh', 'ocean_waves', 'none').

REGLAS CRÍTICAS:
1. **LÍMITE ESTRICTO DE PALABRAS:** La narración completa del video completo sumando todas las escenas **NO DEBE EXCEDER LAS 120 PALABRAS**. Sé ultra directo, conciso y de alto impacto.
2. **COORDEANADAS DE MAPA EXACTAS Y REALISTAS:** Investiga y define coordenadas geográficas correctas de latitud y longitud correspondientes a los lugares de los que se habla en cada escena. ¡Es un video de geografía, la precisión cartográfica es vital!
3. **DISEÑO SONORO COMPLETO:** Elige efectos de sonido (`sfx`) acordes al contenido de la escena para asegurar un diseño de audio envolvente.
4. **INTRIGA EN EL HEADER:** El `intrigue_header` debe ser un título de 3 a 5 palabras en MAYÚSCULAS persistente al inicio (ej: "EL MURO DE COLOMBIA", "EL LUGAR MÁS LLUVIOSO", "EL SECRETO DE LOS ANDES").
5. **CTA AGRESIVO:** Termina el video con un llamado a la acción intrigante que invite al usuario a dejar su opinión o experiencia en los comentarios.
"""
