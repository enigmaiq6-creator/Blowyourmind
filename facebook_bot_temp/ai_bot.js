const { uploadPhoto, uploadPhotoToInstagram } = require('./facebookClient');
const fs = require('fs');
const path = require('path');
const { OpenAI } = require('openai');
const axios = require('axios');
require('dotenv').config();

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

async function downloadImage(url, filepath) {
    const response = await axios({
        url,
        method: 'GET',
        responseType: 'stream'
    });
    return new Promise((resolve, reject) => {
        const writer = fs.createWriteStream(filepath);
        response.data.pipe(writer);
        writer.on('finish', resolve);
        writer.on('error', reject);
    });
}

// =========== CONFIGURACIÓN DEL CONTENIDO =========== //
const SYSTEM_ROLE = "Eres un creador de contenido experto en salud, fitness y curiosidades del cuerpo humano. Haces publicaciones virales y educativas para Facebook 100% en ESPAÑOL.";

function getPromptForContent() {
    const randomSeed = Math.floor(Math.random() * 10000);
    return `Genera un tema ÚNICO y fascinante de salud o hábitos usando la semilla ${randomSeed}. 
    Evita clichés. Busca algo específico y asombroso (ej. medicina antigua, biología celular rara, efectos de un hábito inusual).
    
    RESPONDE ESTRICTAMENTE EN ESTE FORMATO (COPIA Y PEGA):
    TEMA_IMAGEN: [Resumen de 5 palabras para DALL-E en español]
    CONTENIDO_POST: [El post completo para Facebook en español, con datos, consejos y 3 hashtags. Sin saludos genéricos.]`;
}

function getImagePrompt(topic) {
    const styles = [
        "Infografía minimalista profesional, sin texto o con texto mínimo en ESPAÑOL.",
        "Ilustración médica 3D realista con colores vibrantes.",
        "Fotografía macro de alta definición estilo National Geographic.",
        "Diseño gráfico vectorizado moderno y limpio."
    ];
    const style = styles[Math.floor(Math.random() * styles.length)];
    return `Imagen sobre: ${topic}. Estilo: ${style}. 
    REGLA CRÍTICA: La imagen debe ser 100% visual. SI USAS TEXTO, debe ser máximo 2 palabras y ESTRICTAMENTE EN ESPAÑOL. 
    PROHIBIDO EL INGLÉS. Calidad premium, 4k, profesional.`;
}

async function generateAndPost() {
    try {
        console.log('🤖 Generando idea y texto...');
        const textCompletion = await openai.chat.completions.create({
            model: "gpt-4-turbo",
            messages: [
                { role: "system", content: SYSTEM_ROLE },
                { role: "user", content: getPromptForContent() }
            ]
        });
        
        const rawResponse = textCompletion.choices[0].message.content;
        console.log('--- RESPUESTA AI ---');
        console.log(rawResponse);

        // Extraer tema y contenido
        const topicMatch = rawResponse.match(/TEMA_IMAGEN:\s*(.*)/i);
        const postMatch = rawResponse.match(/CONTENIDO_POST:\s*([\s\S]*)/i);

        const topic = topicMatch ? topicMatch[1].trim() : "Salud y bienestar";
        const description = postMatch ? postMatch[1].trim() : rawResponse;

        console.log(`✅ Tema para imagen: ${topic}`);

        console.log('🎨 Generando imagen coordinada con el tema...');
        const imageResponse = await openai.images.generate({
            model: "dall-e-3",
            prompt: getImagePrompt(topic),
            n: 1,
            size: "1024x1024",
        });

        const imageUrl = imageResponse.data[0].url;
        const filepath = path.join(__dirname, 'content', `post_${Date.now()}.png`);
        
        if (!fs.existsSync(path.join(__dirname, 'content'))) {
            fs.mkdirSync(path.join(__dirname, 'content'));
        }

        console.log('⬇️ Descargando imagen...');
        await downloadImage(imageUrl, filepath);

        if (!fs.existsSync(filepath)) throw new Error('Error al descargar imagen');

        if (!process.env.PAGE_ACCESS_TOKEN) {
            console.log('⚠️ Sin token de FB. Proceso local terminado.');
            return;
        }

        console.log('🚀 Publicando en Facebook e Instagram...');
        await uploadPhoto(filepath, description);
        
        // Crosspost a Instagram (usamos la URL de OpenAI directamente que es pública)
        try {
            console.log('⏳ Esperando 5 segundos antes de publicar en Instagram...');
            await new Promise(resolve => setTimeout(resolve, 5000));
            await uploadPhotoToInstagram(imageUrl, description);
        } catch (igError) {
            console.warn('⚠️ Falló publicación en Instagram:', igError.response ? JSON.stringify(igError.response.data) : igError.message);
            console.warn('Facebook OK, pero verifica los permisos de Instagram.');
        }

        console.log('🎉 ¡Proceso completado con éxito!');
        
    } catch (error) {
        console.error('❌ Error en el proceso:');
        if (error.response && error.response.data) {
            console.error(JSON.stringify(error.response.data, null, 2));
        } else {
            console.error(error.message);
        }
        throw error; // Lanzar el error para que GitHub Actions marque el job como fallido
    }
}

generateAndPost().then(() => {
    console.log('🏁 Bot execution finished.');
}).catch(err => {
    console.error('💥 Fatal error in bot execution:', err);
    process.exit(1);
});
