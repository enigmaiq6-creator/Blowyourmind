const axios = require('axios');
require('dotenv').config();

const userToken = process.env.PAGE_ACCESS_TOKEN;
const pageId = process.env.PAGE_ID;

async function exchangeToken() {
    try {
        console.log(`--- Exchanging Token for Page ID: ${pageId} ---`);
        const response = await axios.get(`https://graph.facebook.com/${pageId}`, {
            params: {
                fields: 'access_token',
                access_token: userToken
            }
        });
        
        const pageAccessToken = response.data.access_token;
        if (!pageAccessToken) {
            console.error('No se pudo obtener el Token de Página. Respuesta:', response.data);
            return;
        }

        console.log(`✅ Token de Página obtenido con éxito!`);
        console.log(`Token: ${pageAccessToken}`);
        
        // No imprimimos el token completo en producción, pero aquí lo necesitamos para el siguiente comando
    } catch (error) {
        console.error('Error en el intercambio:', error.response ? error.response.data : error.message);
    }
}

exchangeToken();
