// --- UNIVERSAL HYBRID BOT (LOCAL + DRIVE) ---
const { OpenAI } = require('openai');
const { uploadVideo, uploadReelToInstagram, uploadToTempHost } = require('./facebookClient');
const { getFirstVideo, downloadVideo, moveFile } = require('./googleDriveClient');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

// Persistent logging helper
function log(message, type = 'INFO') {
    const timestamp = new Date().toLocaleString();
    const logMessage = `[${timestamp}] [${type}] ${message}\n`;
    console.log(logMessage.trim());
    try {
        fs.appendFileSync('automator.log', logMessage);
    } catch (e) {
        // Fallback if log file fails
    }
}

async function generateVideoSEO(filename) {
    if (!process.env.OPENAI_API_KEY || process.env.OPENAI_API_KEY.trim() === '') {
        log('⚠️ No OPENAI_API_KEY found. Usando fallback SEO.', 'WARN');
        const topic = filename.replace(/\.(mp4|mov|avi)$/i, "").replace(/[-_]/g, " ").trim();
        return {
            title: topic.charAt(0).toUpperCase() + topic.slice(1),
            description: `✨ ${topic.charAt(0).toUpperCase() + topic.slice(1)}\n\n#viral #contenido #video`
        };
    }

    const topic = filename.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
    const prompt = `Actúa como un experto en redes sociales y SEO. El tema del video es: "${topic}".
    1. Título atractivo (máximo 60 caracteres).
    2. Descripción viral (2 párrafos con emojis).
    3. 5 hashtags optimizados.
    FORMATO: TITULO: [titulo] DESCRIPCION: [descripcion]`;

    try {
        const completion = await openai.chat.completions.create({
            model: "gpt-4-turbo",
            messages: [{ role: "user", content: prompt }]
        });
        const rawResponse = completion.choices[0].message.content;
        const titleMatch = rawResponse.match(/TITULO:\s*(.*)/i);
        const descMatch = rawResponse.match(/DESCRIPCION:\s*([\s\S]*)/i);
        return {
            title: titleMatch ? titleMatch[1].trim() : topic,
            description: descMatch ? descMatch[1].trim() : `🎥 ${topic}`
        };
    } catch (e) {
        log(`Error OpenAI: ${e.message}`, 'ERROR');
        return { title: topic, description: `🎥 ${topic}` };
    }
}

async function runVideoBot() {
    log('--- Iniciando Ciclo de Publicación ---');
    let videoFile = null;
    let isLocal = false;
    const contentDir = path.join(__dirname, 'content');
    const processedDir = path.join(contentDir, 'processed');

    if (!fs.existsSync(contentDir)) fs.mkdirSync(contentDir);
    if (!fs.existsSync(processedDir)) fs.mkdirSync(processedDir);

    // 1. ESCANEO LOCAL (Prioridad)
    const localFiles = fs.readdirSync(contentDir).filter(f => f.match(/\.(mp4|mov|avi)$/i));
    if (localFiles.length > 0) {
        const fileName = localFiles[0];
        videoFile = { name: fileName, path: path.join(contentDir, fileName) };
        isLocal = true;
        log(`📂 Video local detectado: ${fileName}`);
    } 

    // 2. ESCANEO DRIVE (Si no hay local)
    if (!videoFile) {
        const PENDING_FOLDER_ID = process.env.DRIVE_PENDING_FOLDER_ID;
        if (PENDING_FOLDER_ID) {
            const driveFile = await getFirstVideo(PENDING_FOLDER_ID);
            if (driveFile) {
                log(`☁️ Video en Drive detectated: ${driveFile.name}`);
                const destPath = path.join(contentDir, `drive_${Date.now()}_${driveFile.name}`);
                await downloadVideo(driveFile.id, destPath);
                videoFile = { name: driveFile.name, path: destPath, id: driveFile.id };
            }
        }
    }

    if (!videoFile) {
        log('😴 No hay videos pendientes ni locales ni en Drive.', 'INFO');
        return;
    }

    try {
        // 3. Generar SEO
        const seoData = await generateVideoSEO(videoFile.name);
        
        // 4. Subir a Facebook
        log(`🚀 Publicando en Facebook: ${seoData.title}`);
        await uploadVideo(videoFile.path, seoData.description, seoData.title);
        
        // 5. Instagram
        try {
            log('📸 Intentando publicación en Instagram Reels...');
            const tempUrl = await uploadToTempHost(videoFile.path);
            if (tempUrl) await uploadReelToInstagram(tempUrl, seoData.description);
        } catch (igError) {
            log(`⚠️ Instagram falló: ${igError.message}`, 'WARN');
        }

        // 6. Limpieza / Movimiento
        if (isLocal) {
            fs.renameSync(videoFile.path, path.join(processedDir, videoFile.name));
            log(`✅ Video local movido a /processed`);
        } else {
            const PENDING = process.env.DRIVE_PENDING_FOLDER_ID;
            const PUBLISHED = process.env.DRIVE_PUBLISHED_FOLDER_ID;
            await moveFile(videoFile.id, PENDING, PUBLISHED);
            fs.unlinkSync(videoFile.path);
            log(`✅ Video de Drive procesado y movido en la nube`);
        }

        log('🎉 Publicación exitosa.');
    } catch (error) {
        log(`❌ Error crítico en runVideoBot: ${error.message}`, 'ERROR');
        throw error;
    }
}

const FIVE_HOURS = 5 * 60 * 60 * 1000;

async function startLoop() {
    log('🤖 Bot Híbrido Iniciado. Modo: Loop infinito (5h)');
    
    while (true) {
        try {
            await runVideoBot();
        } catch (error) {
            log(`💥 Error en ciclo: ${error.message}`, 'ERROR');
        }
        const nextRun = new Date(Date.now() + FIVE_HOURS);
        log(`⏳ Siguiente ejecución: ${nextRun.toLocaleTimeString()}`);
        await new Promise(resolve => setTimeout(resolve, FIVE_HOURS));
    }
}

// Determinar si corre en loop o una sola vez (para GitHub Actions)
if (process.env.GITHUB_ACTIONS || process.env.ONCE) {
    log('🚀 Ejecución única detectada (Cloud/Manual)');
    runVideoBot();
} else {
    startLoop();
}
