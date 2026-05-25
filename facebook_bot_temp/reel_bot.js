const fs = require('fs');
const path = require('path');
const axios = require('axios');
const { execSync } = require('child_process');
const AudioService = require('./audioService');
const ImageService = require('./imageService');
const TopicManager = require('./topicManager');
require('dotenv').config();

const { OpenAI } = require('openai');
const client = new OpenAI({
    apiKey: process.env.GROQ_API_KEY,
    baseURL: "https://api.groq.com/openai/v1"
});

const { uploadReelToFacebook } = require('./facebookClient');

// Configuración de rutas (Inteligencia Nube/Local)
const isCloud = process.platform === 'linux';
const FFMPEG_PATH = isCloud ? 'ffmpeg' : `C:\\Users\\Marlys\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.1-full_build\\bin\\ffmpeg.exe`;
const CONTENT_DIR = path.join(__dirname, 'content', 'reels_v2');
if (!fs.existsSync(CONTENT_DIR)) fs.mkdirSync(CONTENT_DIR, { recursive: true });

async function createReelProV5() {
    try {
        console.log('🚀 Lanzando EnigmaIQ V5.3 COHERENCIA REAL (Autonomía Total)...');
        
        // Generar semilla para el búnker local para evitar repeticiones entre videos
        const bunkerSeed = Math.floor(Math.random() * 18);
        
        // 1. Obtener tema del Cerebro (TopicManager)
        const topicData = TopicManager.getTopic();
        console.log(`📡 Nicho Elegido: ${topicData.niche} (${topicData.visualStyle})`);
        console.log(`🤖 Generando guion educativo de alto RPM...`);
        
        const completion = await client.chat.completions.create({
            model: "llama-3.3-70b-versatile",
            messages: [
                { 
                    role: "system", 
                    content: `Eres un guionista experto en Reels virales de alto RPM para 'EnigmaIQ'. 
                    Tu nicho hoy es: ${topicData.niche} (${topicData.nicheDesc}).
                    Estilo visual: ${topicData.visualStyle}.
                    
                    REGLA DE ORO VISUAL: Genera prompts de imagen REALISTAS y LITERALES. 
                    PROHIBIDO lo abstracto, lo metafórico o lo artístico confuso.
                    Si hablas de salud, muestra un laboratorio real o un médico real.
                    Si hablas de éxito, muestra dinero real o personas reales trabajando.
                    
                    Estructura: Gancho -> Problema -> REVELACIÓN CLARA -> CTA.
                    Idioma: Latino Alegre y Profesional.` 
                },
                { 
                    role: "user", 
                    content: `Genera un guion de 6 ESCENAS único sobre el nicho ${topicData.niche}. 
                    Cada escena debe tener 25-30 palabras. 
                    REVELA el secreto en las escenas 4 y 5.
                    AÑADE AL FINAL una descripción viral para Facebook llena de hashtags y ganchos. IMPORTANTE: NO escribas la frase "DESCRIPCIÓN VIRAL:" ni ningún prefijo, ve directo al texto persuasivo.
                    Formato: ESCENA X | [Texto] | [Prompt Visual Realista] | [Emoción]` 
                }
            ]
        });

        const rawScript = completion.choices[0].message.content;
        console.log('--- GUION AUTÓNOMO GENERADO ---');
        console.log(rawScript);



        const lines = rawScript.split('\n').filter(l => l.includes('|'));
        // Intentar extraer una descripción limpia de la IA
        let socialCaption = `🌟 DISCOVER: ${topicData.niche} 🌟\n\nSecretos revelados en EnigmaIQ. #Salud #Misterio #IA #Viral`;
        const scriptLines = rawScript.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        const lastLine = scriptLines[scriptLines.length - 1];
        if (lastLine && !lastLine.includes('|') && lastLine.length > 20) {
            // Limpieza agresiva de cualquier prefijo robótico
            socialCaption = lastLine.replace(/^(DESCRIPCI[OÓ]N( VIRAL)?|CAPTION|POST|TEXTO)( PARA FACEBOOK)?:?\s*-?\s*/i, '');
        }

        const scenes = lines.map(line => {
            const parts = line.split('|').map(p => p.trim());
            if (parts.length < 4) return null;
            return {
                text: parts[1],
                prompt: parts[2],
                emotion: parts[3].toLowerCase()
            };
        }).filter(s => s !== null);

        if (scenes.length === 0) throw new Error("Guion malformado.");

        console.log(`🎬 Guion listo: ${scenes.length} escenas. Iniciando producción...`);
        const sceneClips = [];

        for (let i = 0; i < scenes.length; i++) {
            const scene = scenes[i];
            const index = i + 1;
            console.log(`\n--- ESCENA ${index}/6 ---`);

            // 1. Audio y SRT
            const audioPath = path.join(CONTENT_DIR, `audio_${index}.mp3`);
            const srtPath = path.join(CONTENT_DIR, `subs_${index}.srt`);
            await AudioService.generateAudio(scene.text, audioPath, srtPath, scene.emotion);

            // 2. Imagen con Estilo Dinámico (Calidad o Nada)
            const imagePath = path.join(CONTENT_DIR, `image_${index}.png`);
            await ImageService.generateImageWithFallback(scene.prompt, imagePath, index, topicData.visualStyle);

            // 3. Crear micro-clip con Subtítulos Sincronizados
            console.log(`🎬 Compilando clip con estilo ${topicData.visualStyle}...`);
            const clipPath = path.join(CONTENT_DIR, `clip_${index}.mp4`);
            
            // Escapar ruta SRT para FFmpeg en Windows
            const srtPathEscaped = srtPath.replace(/\\/g, '/').replace(/:/g, '\\:');

            const ffmpegCmd = `"${FFMPEG_PATH}" -loop 1 -i "${imagePath}" -i "${audioPath}" -vf "scale=2160x3840,zoompan=z='min(zoom+0.0008,1.2)':d=125:s=1080x1920:fps=25,subtitles='${srtPathEscaped}':force_style='Alignment=2,FontSize=28,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2,MarginV=60'" -c:v libx264 -c:a aac -shortest -pix_fmt yuv420p -y "${clipPath}"`;
            
            execSync(ffmpegCmd);
            sceneClips.push(clipPath);
            
            // Pausa de cortesía para las APIs
            await new Promise(r => setTimeout(r, 2000));
        }

        // 4. Concatenación Final
        console.log('\n🔗 Uniendo los 6 capítulos del Reel Pro...');
        const finalVideo = path.join(__dirname, 'content', `reel_pro_v4_${Date.now()}.mp4`);
        const concatListPath = path.join(CONTENT_DIR, 'list.txt');
        const listContent = sceneClips.map(c => `file '${c.replace(/\\/g, '/')}'`).join('\n');
        fs.writeFileSync(concatListPath, listContent);

        const concatCmd = `"${FFMPEG_PATH}" -f concat -safe 0 -i "${concatListPath}" -c copy -y "${finalVideo}"`;
        execSync(concatCmd);

        console.log('🚀 Subiendo Reel a Facebook API Oficial...');
        await uploadReelToFacebook(finalVideo, socialCaption);

        // Registro de éxito
        TopicManager.saveToHistory(scenes[0].text, topicData.niche);
        console.log('🎉 ¡REEL PUBLICADO CON ÉXITO! Calidad 100% garantizada.');

    } catch (error) {
        console.log('\n🛑 PRODUCCIÓN CANCELADA 🛑');
        console.error('⚠️ Motivo Calidad:', error.message);
        console.log('El video no ha sido publicado en Facebook por no cumplir los estándares.');
    }
}

createReelProV5();


