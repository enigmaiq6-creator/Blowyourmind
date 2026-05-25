# 🏗️ AI Content Automation Engine - Guía de Arquitectura Híbrida

Este documento detalla la estructura final de la infraestructura del bot automatizado, cómo superamos los límites de cuota y cómo está configurada la autenticación en GitHub Actions. **Guarda este documento como referencia en caso de que necesites migrar el bot o arreglar problemas futuros.**

## 1. El Problema Original: Límites de Cuota (Error 429)
El diseño original del bot utilizaba **Google AI Studio (API Key gratuita)** para absolutamente todo: pensar guiones, generar audio, y generar imágenes. Al producir videos complejos de 10 escenas, la cantidad de peticiones por minuto superaba el límite de la capa gratuita, resultando en baneos temporales (`429 RESOURCE_EXHAUSTED`).

## 2. La Solución: Arquitectura Híbrida (AI Studio + Vertex AI)
Para tener un sistema 100% autónomo y evitar cobros excesivos, dividimos el cerebro del bot en dos vías separadas que funcionan en paralelo:

### A. Vía Gratuita (Google AI Studio)
Se utiliza exclusivamente para **Texto (Guiones)** y **Audio (Voz)**.
- **Modelo de Texto:** `gemini-2.5-flash` (Tiene una cuota amplia y gratuita separada).
- **Modelo de Audio:** `gemini-2.5-flash-preview-tts` (La voz hiperrealista de "Fenrir" solo existe en este entorno).
- **Autenticación:** Usa la variable `GEMINI_API_KEY`.

### B. Vía Profesional de Pago (Google Cloud Vertex AI)
Se utiliza exclusivamente para **Imágenes y Video Animado**.
- **Modelos:** `imagen-3.0-generate-001` (Para imágenes estáticas) y `veo-2.0-generate-001` (Para video).
- **Consumo:** Utiliza los créditos gratuitos de prueba ($300 USD) asociados al proyecto de Google Cloud (`automatizacion-475715`).
- **Activación en Código:** Requiere que la variable de entorno `USE_VERTEX_AI_IMAGE` esté configurada en `"true"`.

---

## 3. Configuración de GitHub Actions (`daily_post.yml`)
El archivo de integración continua en `.github/workflows/daily_post.yml` está diseñado para ejecutarse automáticamente cada 6 horas (`cron: '0 */6 * * *'`) o manualmente mediante un botón en la interfaz de GitHub.

### Variables de Entorno Clave en GitHub Secrets
Para que el bot funcione, GitHub necesita los siguientes *Secrets*:
1. `GEMINI_API_KEY`: Llave de Google AI Studio.
2. `GCP_PROJECT_ID`: ID del proyecto (ej: `automatizacion-475715`).
3. `GCP_LOCATION`: Región de Vertex AI (ej: `us-central1`).
4. `GOOGLE_APPLICATION_CREDENTIALS_JSON`: El código JSON completo de la Cuenta de Servicio de Google Cloud.
5. Credenciales de Facebook: `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_ACCESS_TOKEN`, `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`.

### El Parche de Seguridad (Error "PEM Decoder")
**El Problema:** Al copiar el JSON de la Cuenta de Servicio desde Google Cloud hacia GitHub Secrets, los saltos de línea de la llave privada se rompían, causando que la librería criptográfica lanzara el error `DECODER routines::unsupported` o `InvalidByte(1640, 61)`.

**La Solución:** En lugar de usar herramientas estándar de Bash o acciones de terceros que rompen el formato, implementamos un intérprete directo en Python dentro del workflow:
```yaml
      - name: Create GCP Credentials
        env:
          GCP_JSON: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS_JSON }}
        run: |
          python -c "import os, json; f=open('gcp_credentials.json', 'w'); json.dump(json.loads(os.environ.get('GCP_JSON', '{}'), strict=False), f, indent=2)"
          echo "GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/gcp_credentials.json" >> $GITHUB_ENV
```
*Si alguna vez necesitas actualizar la llave en el futuro, simplemente genera un nuevo JSON en Google Cloud, copia el texto y pégalo directamente en el secreto de GitHub. El script de Python anterior se encargará de darle el formato correcto automáticamente.*

---

## 4. Estructura de Tareas Automáticas (El Pipeline)
El código principal (`pipeline.py`) ejecuta 8 pasos secuenciales:

1. **`step1_generate_story()`**: Pide a AI Studio (`gemini-2.5-flash`) que genere un guion de 8-10 escenas en JSON.
2. **`step2_generate_images()`**: Si `USE_VERTEX_AI_IMAGE=true`, envía 10 peticiones a Vertex AI (Imagen 3) usando tus créditos de prueba.
3. **`step3_generate_audios()`**: Pide a AI Studio (`gemini-2.5-flash-preview-tts`) que narre el guion con voz realista, luego usa `Whisper.cpp` para alinear los tiempos exactos.
4. **`step4_generate_videos()`**: Usa `FFmpeg` (instalado en la máquina de GitHub) para unir el audio con la imagen estática y crear el video base.
5. **`step5_generate_subtitles()`**: Incrusta los subtítulos en pantalla usando el mapa de tiempo de Whisper.
6. **`step6_add_background_music()`**: Toma una canción aleatoria de `resource/bg-music`, la baja de volumen y la mezcla de fondo.
7. **`step7_rename_final_video()`**: Empaqueta todo bajo el nombre final SEO-optimizado.
8. **`step8_upload_to_facebook()`**: Genera una descripción larga con llamados a la acción, hashtags, y publica automáticamente el archivo final mediante la API de Graph de Facebook.

## 5. Resumen de Modelos en Uso
Si alguna vez un modelo queda obsoleto y arroja un error `404 Not Found`, actualízalos en sus respectivos archivos:
- **Texto:** `tools/text_generation/gemini.py` -> `text_model: str = "gemini-2.5-flash"`
- **Audio:** `tools/audio_generation/gemini.py` -> `tts_model: str = "gemini-2.5-flash-preview-tts"`
- **Imagen:** `tools/image_generation/vertex_ai.py` -> `model='imagen-3.0-generate-001'`
- **Video:** `tools/image_generation/vertex_ai.py` -> `model='veo-2.0-generate-001'`

## 6. Siguientes Pasos
Mantener monitoreado el consumo en la consola de **Google Cloud Billing**. Las imágenes consumen los créditos gratuitos de prueba ($300). Cuando se agoten, se requerirá tarjeta de crédito o migrar la generación de imágenes nuevamente a un modelo gratuito si está disponible.
