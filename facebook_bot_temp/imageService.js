const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

/**
 * Servicio de generación de imágenes con sistema de respaldo (Fallback).
 * V5.6: Integración NANO BANANA (Google Imagen 3)
 */
class ImageService {
    /**
     * Intento 1: Pollinations AI (Salvavidas Gratuito e Ilimitado)
     */
    static async tryPollinations(prompt, style = "Cinemático") {
        console.log(`   🎨 [1/6] Lanzando Pollinations (Gratis e Ilimitado)...`);
        const seed = Math.floor(Math.random() * 1000000);
        const encodedPrompt = encodeURIComponent(`${prompt}, ${style} style, photorealistic photography, highly detailed, 9:16`);
        const url = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=1080&height=1920&nologo=true&seed=${seed}`;
        const response = await axios.get(url, { responseType: 'arraybuffer', timeout: 15000 });
        return Buffer.from(response.data);
    }

    /**
     * Intento 2: NANO BANANA (Google Gemini Image)
     */
    static async tryNanoBanana(prompt, style = "Cinemático") {
        if (!process.env.GEMINI_API_KEY) throw new Error('GEMINI_API_KEY vacía');
        console.log(`   🎨 [2/6] Intentando Nano Banana (Gemini 3.1)...`);
        try {
            const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
            const model = genAI.getGenerativeModel({ model: "gemini-3.1-flash-image-preview" });
            const result = await model.generateContent({
                contents: [{ role: 'user', parts: [{ text: `${prompt}, ${style} style, realistic photography, 9:16` }] }]
            });
            const response = await result.response;
            if (response.candidates && response.candidates[0].content.parts[0].inlineData) {
                const base64Data = response.candidates[0].content.parts[0].inlineData.data;
                return Buffer.from(base64Data, 'base64');
            }
            throw new Error('Sin datos en Nano Banana.');
        } catch (e) {
            throw new Error(`Nano Banana falló: ${e.message}`);
        }
    }

    /**
     * Intento 3: SiliconFlow (Nivel Pro)
     */
    static async trySiliconFlow(prompt, style = "Cinemático") {
        if (!process.env.SILICONFLOW_KEY) throw new Error('SiliconFlow Key vacía');
        console.log(`   🎨 [3/6] Intentando SiliconFlow (Global)...`);
        const response = await axios.post('https://api.siliconflow.com/v1/images/generations', {
            model: "black-forest-labs/FLUX.1-schnell",
            prompt: `${prompt}, ${style} style, photography, 9:16`,
            image_size: "576x1024",
            batch_size: 1
        }, {
            headers: { 
                'Authorization': `Bearer ${process.env.SILICONFLOW_KEY}`,
                'Content-Type': 'application/json'
            },
            timeout: 25000
        });
        const data = response.data.images || response.data.data;
        const imageUrl = data[0].url;
        const imgResponse = await axios.get(imageUrl, { responseType: 'arraybuffer' });
        return Buffer.from(imgResponse.data);
    }

    /**
     * Intento 4: Together AI
     */
    static async tryTogetherAI(prompt, style = "Cinemático") {
        if (!process.env.TOGETHER_KEY) throw new Error('Together Key vacía');
        console.log(`   🎨 [4/6] Intentando Together AI...`);
        const response = await axios.post('https://api.together.xyz/v1/images/generations', {
            model: "black-forest-labs/FLUX.1-schnell",
            prompt: `${prompt}, ${style} style, photography, 9:16`,
            width: 576,
            height: 1024,
            steps: 4,
            n: 1
        }, {
            headers: { 
                'Authorization': `Bearer ${process.env.TOGETHER_KEY}`,
                'Content-Type': 'application/json'
            },
            timeout: 25000
        });
        const imageUrl = response.data.data[0].url;
        const imgResponse = await axios.get(imageUrl, { responseType: 'arraybuffer' });
        return Buffer.from(imgResponse.data);
    }

    /**
     * Intento 5: Stock Photo Dinámico (Pixabay)
     */
    static async tryStockPhoto(prompt) {
        try {
            console.log('   📸 [5/6] Buscando Stock Real (Pixabay)...');
            const clean = prompt.replace(/style|vertical|cinematic|detailed|background|photography|photorealistic|image/gi, '');
            const keywords = clean.split(' ').filter(w => w.length > 4).slice(0, 2).join(' ');
            const query = encodeURIComponent(keywords || "science technology");
            const url = `https://pixabay.com/api/?key=43525287-2f5cd61c77f0a6711a37a77e8&q=${query}&image_type=photo&orientation=vertical&per_page=3`;
            const response = await axios.get(url, { timeout: 10000 });
            if (response.data.hits && response.data.hits.length > 0) {
                const imgUrl = response.data.hits[0].largeImageURL;
                const imgResponse = await axios.get(imgUrl, { responseType: 'arraybuffer' });
                return Buffer.from(imgResponse.data);
            }
            throw new Error('Sin stock.');
        } catch (e) {
            throw new Error(`Stock falló: ${e.message}`);
        }
    }

    /**
     * Traduce el prompt al inglés para máxima compatibilidad con las APIs de IA.
     */
    static async translateToEnglish(text) {
        try {
            const { OpenAI } = require('openai');
            const groq = new OpenAI({ apiKey: process.env.GROQ_API_KEY, baseURL: "https://api.groq.com/openai/v1" });
            const completion = await groq.chat.completions.create({
                model: "llama-3.3-70b-versatile",
                messages: [{ role: "system", content: "Translate the following image prompt to a concise, descriptive English prompt for AI generation. Just the translation, no extra text." }, { role: "user", content: text }],
                max_tokens: 60
            });
            return completion.choices[0].message.content.trim();
        } catch (e) {
            console.warn('   ⚠️ Error de traducción, usando original:', e.message);
            return text;
        }
    }

    /**
     * MOTOR DE GENERACIÓN V5.11 (BLINDAJE Y REINTENTOS)
     * Realiza 3 intentos por escena antes de abortar.
     */
    static async generateImageWithFallback(prompt, filePath, sceneIndex = 1, style = "Cinemático") {
        console.log(`   🌐 Traduciendo prompt para máxima calidad...`);
        const englishPrompt = await this.translateToEnglish(prompt);
        console.log(`   💡 English Prompt: ${englishPrompt}`);

        const methods = [
            async (seed) => {
                console.log(`   🎨 Intentando Pollinations (Seed: ${seed})...`);
                const encoded = encodeURIComponent(`${englishPrompt}, ${style} style, photography, highly detailed, photorealistic`);
                // Optimización Turbo: 512x912 para velocidad extrema, FFmpeg lo escalará. Tiempo de espera subido a 45s.
                const url = `https://image.pollinations.ai/prompt/${encoded}?width=512&height=912&nologo=true&seed=${seed}`;
                const response = await axios.get(url, { responseType: 'arraybuffer', timeout: 45000 });
                return Buffer.from(response.data);
            },
            () => this.tryStockPhoto(englishPrompt),
            async (seed) => {
                console.log('   📸 [Respaldo Invencible] Activando Lorem Picsum (Unsplash)...');
                const url = `https://picsum.photos/seed/${seed}/1080/1920`;
                const response = await axios.get(url, { responseType: 'arraybuffer', timeout: 15000 });
                return Buffer.from(response.data);
            }
        ];

        // 3 Intentos totales por escena
        for (let attempt = 1; attempt <= 3; attempt++) {
            console.log(`   🔄 Intento ${attempt}/3 por la Escena ${sceneIndex}...`);
            const currentSeed = Math.floor(Math.random() * 1000000);
            
            for (const method of methods) {
                try {
                    const buffer = await method(currentSeed);
                    fs.writeFileSync(filePath, buffer);
                    console.log(`   ✅ Imagen lograda con éxito en el intento ${attempt}.`);
                    return true;
                } catch (error) {
                    // Solo logueamos si es el último método
                    if (method === methods[methods.length - 1]) {
                        console.warn(`   ⏳ Intento ${attempt} fallido, probando de nuevo...`);
                    }
                }
            }
            // Espera de cortesía entre reintentos
            await new Promise(r => setTimeout(r, 2000));
        }

        throw new Error('FAIL: Todas las APIs y reintentos fallaron para esta escena.');
    }
}

module.exports = ImageService;
