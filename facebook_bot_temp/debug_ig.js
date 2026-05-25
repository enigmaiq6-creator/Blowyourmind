const axios = require('axios');
require('dotenv').config();

const token = process.env.PAGE_ACCESS_TOKEN;
const igId = process.env.INSTAGRAM_BUSINESS_ID;

async function debugIG() {
    try {
        console.log(`--- Debugging Instagram ID: ${igId} ---`);
        const response = await axios.get(`https://graph.facebook.com/v20.0/${igId}`, {
            params: {
                fields: 'id,username,name,website',
                access_token: token
            }
        });
        console.log('✅ Información de la cuenta IG encontrada:');
        console.log(JSON.stringify(response.data, null, 2));

        console.log('\n--- Probando permisos de publicación en IG (container check) ---');
        // Solo probamos crear un contenedor (sin publicar) para ver si da error de permisos
        try {
            const check = await axios.post(`https://graph.facebook.com/v20.0/${igId}/media`, null, {
                params: {
                    image_url: 'https://raw.githubusercontent.com/danielfe125050-lab/facebook-ai-bot/main/content/sample.png', // Solo una URL de prueba
                    caption: 'Test',
                    access_token: token
                }
            });
            console.log('✅ Parece que sí tienes permisos para crear contenedores!');
        } catch (e) {
            console.error('❌ Error de permisos al intentar crear contenedor:');
            console.error(JSON.stringify(e.response ? e.response.data : e.message, null, 2));
        }

    } catch (error) {
        console.error('❌ Error al consultar la cuenta IG:');
        console.error(JSON.stringify(error.response ? error.response.data : error.message, null, 2));
    }
}

debugIG();
