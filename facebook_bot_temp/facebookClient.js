const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const PAGE_ACCESS_TOKEN = process.env.PAGE_ACCESS_TOKEN;
const PAGE_ID = process.env.PAGE_ID;

if (!PAGE_ACCESS_TOKEN || !PAGE_ID) {
    console.warn('Warning: PAGE_ACCESS_TOKEN or PAGE_ID not found in .env file. Facebook uploads will fail.');
}

const api = axios.create({
    baseURL: 'https://graph.facebook.com/v19.0',
    params: {
        access_token: PAGE_ACCESS_TOKEN
    }
});

const videoApi = axios.create({
    baseURL: 'https://graph-video.facebook.com/v19.0',
    params: {
        access_token: PAGE_ACCESS_TOKEN
    }
});

async function uploadPhoto(filePath, caption = '') {
    try {
        console.log(`Uploading photo: ${filePath}...`);
        const form = new FormData();
        form.append('source', fs.createReadStream(filePath));
        form.append('message', caption);
        // published: true is default, but we can set published: false and scheduled_publish_time for scheduling

        const response = await api.post(`/${PAGE_ID}/photos`, form, {
            headers: form.getHeaders()
        });

        console.log(`Photo uploaded successfully! ID: ${response.data.id}`);
        return response.data;
    } catch (error) {
        console.error('Error uploading photo:', error.response ? error.response.data : error.message);
        throw error;
    }
}

async function uploadPhotoByUrl(url, caption = '') {
    try {
        console.log(`Uploading photo from URL: ${url}...`);
        
        const response = await api.post(`/${PAGE_ID}/photos`, {
            url: url,
            message: caption
        });

        console.log(`Photo uploaded successfully via URL! ID: ${response.data.id}`);
        return response.data;
    } catch (error) {
        console.error('Error uploading photo by URL:', error.response ? error.response.data : error.message);
        throw error;
    }
}

async function uploadVideo(filePath, description = '', title = '') {
    const stats = fs.statSync(filePath);
    const fileSize = stats.size;
    const CHUNK_SIZE = 10 * 1024 * 1024; // 10MB por chunk

    try {
        console.log(`🚀 Iniciando subida de video por partes: ${filePath} (${(fileSize / 1024 / 1024).toFixed(2)} MB)...`);
        
        // 1. Fase START
        const startResponse = await videoApi.post(`/${PAGE_ID}/videos`, null, {
            params: {
                upload_phase: 'start',
                file_size: fileSize,
                access_token: PAGE_ACCESS_TOKEN
            }
        });

        const { upload_session_id, video_id } = startResponse.data;
        console.log(`   Sesión iniciada: ${upload_session_id}`);

        // 2. Fase TRANSFER (En chunks)
        let startOffset = 0;
        const fileBuffer = fs.readFileSync(filePath);

        while (startOffset < fileSize) {
            const endOffset = Math.min(startOffset + CHUNK_SIZE, fileSize);
            const chunk = fileBuffer.slice(startOffset, endOffset);

            console.log(`   Subiendo bloque: ${startOffset} - ${endOffset} (${((startOffset / fileSize) * 100).toFixed(0)}%)...`);
            
            const form = new FormData();
            form.append('upload_phase', 'transfer');
            form.append('upload_session_id', upload_session_id);
            form.append('start_offset', startOffset.toString());
            form.append('video_file_chunk', chunk, { filename: 'chunk.mp4' });

            await videoApi.post(`/${PAGE_ID}/videos`, form, {
                headers: form.getHeaders(),
                maxContentLength: Infinity,
                maxBodyLength: Infinity
            });

            startOffset = endOffset;
        }

        console.log('   Transferencia completa.');

        // 3. Fase FINISH
        const finishParams = {
            upload_phase: 'finish',
            upload_session_id: upload_session_id,
            description: description,
            access_token: PAGE_ACCESS_TOKEN
        };
        if (title) finishParams.title = title;

        const finishResponse = await videoApi.post(`/${PAGE_ID}/videos`, null, {
            params: finishParams
        });

        if (finishResponse.data.success) {
            console.log(`✅ Video publicado con éxito! ID: ${video_id}`);
            return { id: video_id };
        } else {
            throw new Error('La fase final de subida no devolvió éxito.');
        }
    } catch (error) {
        console.error('❌ Error uploading video:', error.response ? JSON.stringify(error.response.data) : error.message);
        throw error;
    }
}

async function uploadPhotoToInstagram(imageUrl, caption = '') {
    const instagramId = process.env.INSTAGRAM_BUSINESS_ID;
    if (!instagramId) {
        console.warn('⚠️ INSTAGRAM_BUSINESS_ID no configurado. Saltando Instagram.');
        return null;
    }

    try {
        console.log(`📸 Subiendo foto a Instagram (${instagramId})...`);
        
        // 1. Crear contenedor
        const container = await api.post(`/${instagramId}/media`, null, {
            params: {
                image_url: imageUrl,
                caption: caption,
                access_token: PAGE_ACCESS_TOKEN
            }
        });

        const creationId = container.data.id;

        // 2. Esperar a que la foto esté lista (a veces tarda unos segundos)
        console.log('⏳ Verificando estado de la foto...');
        let status = 'IN_PROGRESS';
        let retries = 0;
        const maxRetries = 10;
        
        while (status !== 'FINISHED' && status !== 'PUBLISHED' && retries < maxRetries) {
            await new Promise(resolve => setTimeout(resolve, 5000)); // Esperar 5s entre chequeos
            try {
                const check = await api.get(`/${creationId}`, {
                    params: { fields: 'status_code', access_token: PAGE_ACCESS_TOKEN }
                });
                status = check.data.status_code;
                console.log(`   Estado foto: ${status}`);
                if (status === 'FINISHED' || status === 'PUBLISHED') break;
                if (status === 'ERROR') throw new Error('Error en el procesamiento de la foto por parte de Instagram.');
            } catch (e) {
                console.warn(`   Intento ${retries + 1} fallido al consultar estado (puede ser transitorio).`);
            }
            retries++;
        }

        // 3. Publicar (Con reintentos por si hay errores de servidor transitorios - Código 2)
        console.log('🚀 Publicando contenedor en el feed...');
        let publish;
        let publishRetries = 0;
        while (publishRetries < 3) {
            try {
                publish = await api.post(`/${instagramId}/media_publish`, null, {
                    params: {
                        creation_id: creationId,
                        access_token: PAGE_ACCESS_TOKEN
                    }
                });
                break; // Éxito
            } catch (err) {
                publishRetries++;
                const isTransient = err.response && err.response.data && err.response.data.error && err.response.data.error.is_transient;
                const errorCode = err.response && err.response.data && err.response.data.error && err.response.data.error.code;
                
                if ((isTransient || errorCode === 2) && publishRetries < 3) {
                    console.warn(`⚠️ Error transitorio en Instagram (Intento ${publishRetries}). Reintentando en 10s...`);
                    await new Promise(resolve => setTimeout(resolve, 10000));
                } else {
                    throw err;
                }
            }
        }

        console.log(`✅ Foto en Instagram publicada! ID: ${publish.data.id}`);
        return publish.data;
    } catch (error) {
        console.error('❌ Error en Instagram Photo:', error.response ? JSON.stringify(error.response.data) : error.message);
        throw error;
    }
}

async function uploadReelToInstagram(videoUrl, caption = '') {
    const instagramId = process.env.INSTAGRAM_BUSINESS_ID;
    if (!instagramId) {
        console.warn('⚠️ INSTAGRAM_BUSINESS_ID no configurado. Saltando Instagram.');
        return null;
    }

    try {
        console.log(`🎬 Subiendo Reel a Instagram (${instagramId})...`);

        // 1. Crear contenedor de Reel
        const container = await api.post(`/${instagramId}/media`, null, {
            params: {
                media_type: 'REELS',
                video_url: videoUrl,
                caption: caption,
                access_token: PAGE_ACCESS_TOKEN
            }
        });

        const creationId = container.data.id;

        // 2. Esperar a que el video sea procesado (los Reels pueden tardar bastante)
        console.log('⏳ Esperando procesamiento de Instagram (hasta 5 min)...');
        let status = 'IN_PROGRESS';
        let startTime = Date.now();
        const timeout = 300000; // 5 minutos
        
        while (status !== 'FINISHED' && status !== 'PUBLISHED') {
            await new Promise(resolve => setTimeout(resolve, 15000)); // 15s entre chequeos para videos
            
            try {
                const check = await api.get(`/${creationId}`, {
                    params: { fields: 'status_code', access_token: PAGE_ACCESS_TOKEN }
                });
                status = check.data.status_code;
                console.log(`   Estado Reel: ${status}`);
                
                if (status === 'FINISHED' || status === 'PUBLISHED') break;
                if (status === 'ERROR') throw new Error('Instagram rechazó el procesamiento del video. Revisa el formato/bitrate.');
            } catch (e) {
                console.warn('   Fallo temporal al consultar estado del Reel.');
            }
            
            if (Date.now() - startTime > timeout) {
                throw new Error('Timeout esperando el procesamiento del Reel en Instagram.');
            }
        }

        // 3. Publicar (Con reintentos)
        console.log('🚀 Publicando Reel en el feed...');
        let publish;
        let publishRetries = 0;
        while (publishRetries < 3) {
            try {
                publish = await api.post(`/${instagramId}/media_publish`, null, {
                    params: {
                        creation_id: creationId,
                        access_token: PAGE_ACCESS_TOKEN
                    }
                });
                break;
            } catch (err) {
                publishRetries++;
                if (publishRetries < 3) {
                    console.warn(`⚠️ Intento ${publishRetries} de publicación de Reel fallido. Reintentando en 15s...`);
                    await new Promise(resolve => setTimeout(resolve, 15000));
                } else {
                    throw err;
                }
            }
        }

        console.log(`✅ Reel en Instagram publicado! ID: ${publish.data.id}`);
        return publish.data;
    } catch (error) {
        console.error('❌ Error en Instagram Reel:', error.response ? JSON.stringify(error.response.data) : error.message);
        throw error;
    }
}

async function uploadToTempHost(filePath) {
    const fileName = path.basename(filePath);
    
    // Intento 1: Catbox.moe (Muy estable para videos)
    try {
        console.log('☁️ Intentando subir a Catbox.moe...');
        const form = new FormData();
        form.append('reqtype', 'fileupload');
        form.append('fileToUpload', fs.createReadStream(filePath));
        
        const response = await axios.post('https://catbox.moe/user/api.php', form, {
            headers: form.getHeaders(),
            maxContentLength: Infinity,
            maxBodyLength: Infinity
        });
        
        if (typeof response.data === 'string' && response.data.startsWith('http')) {
            console.log(`✅ Archivo en Catbox: ${response.data.trim()}`);
            return response.data.trim();
        }
    } catch (e) {
        console.warn('⚠️ Falló Catbox, intentando siguiente...');
    }

    // Intento 2: Transfer.sh (Rápido y soporta archivos grandes)
    try {
        console.log('☁️ Intentando subir a Transfer.sh...');
        const fileStream = fs.createReadStream(filePath);
        const response = await axios.put(`https://transfer.sh/${fileName}`, fileStream, {
            headers: { 'Content-Type': 'application/octet-stream' },
            maxContentLength: Infinity,
            maxBodyLength: Infinity
        });
        
        if (response.data && response.data.startsWith('http')) {
            console.log(`✅ Archivo en Transfer.sh: ${response.data.trim()}`);
            return response.data.trim();
        }
    } catch (e) {
        console.warn('⚠️ Falló Transfer.sh, intentando siguiente...');
    }

    // Intento 3: File.io (Lado seguro)
    try {
        console.log('☁️ Intentando subir a File.io...');
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        const response = await axios.post('https://file.io', form, {
            headers: form.getHeaders()
        });
        if (response.data && response.data.success) {
            console.log(`✅ Archivo en File.io: ${response.data.link}`);
            return response.data.link;
        }
    } catch (error) {
        console.warn('⚠️ Todos los servidores temporales fallaron.');
    }
    
    return null;
}

module.exports = {
    uploadPhoto,
    uploadPhotoByUrl,
    uploadVideo,
    uploadPhotoToInstagram,
    uploadReelToInstagram,
    uploadToTempHost
};
