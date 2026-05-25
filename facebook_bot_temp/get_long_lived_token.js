const axios = require('axios');
require('dotenv').config();

/**
 * Script para obtener un Long-Lived Page Access Token
 * 
 * INSTRUCCIONES:
 * 1. Asegúrate de tener APP_ID y APP_SECRET en tu .env (los obtienes en developers.facebook.com)
 * 2. Asegúrate de tener el PAGE_ACCESS_TOKEN actual (aunque sea de corta duración)
 * 3. Ejecuta: node get_long_lived_token.js
 */

const APP_ID = process.env.APP_ID;
const APP_SECRET = process.env.APP_SECRET;
const SHORT_LIVED_TOKEN = process.env.PAGE_ACCESS_TOKEN;

async function getLongLivedToken() {
    if (!APP_ID || !APP_SECRET || !SHORT_LIVED_TOKEN) {
        console.error('❌ Faltan configuraciones en el .env (APP_ID, APP_SECRET o PAGE_ACCESS_TOKEN)');
        return;
    }

    try {
        console.log('⏳ Depurando token...');
        const appToken = `${APP_ID}|${APP_SECRET}`;
        const debugResponse = await axios.get('https://graph.facebook.com/debug_token', {
            params: {
                input_token: SHORT_LIVED_TOKEN.trim(),
                access_token: appToken.trim()
            }
        });

        console.log('✅ Detalles del token:');
        console.log(JSON.stringify(debugResponse.data.data, null, 2));

        const tokenType = debugResponse.data.data.type; // 'USER' or 'PAGE'
        
        if (tokenType === 'PAGE') {
            console.log('⚠️ El token proporcionado es de PÁGINA. El intercambio directo suele requerir un token de USUARIO.');
        }

        console.log('\n⏳ Paso 1: Intentando intercambio de token...');
        
        // El endpoint estándar para intercambio de tokens es /oauth/access_token
        const userTokenResponse = await axios.get('https://graph.facebook.com/v19.0/oauth/access_token', {
            params: {
                grant_type: 'fb_exchange_token',
                client_id: APP_ID.trim(),
                client_secret: APP_SECRET.trim(),
                fb_exchange_token: SHORT_LIVED_TOKEN.trim()
            }
        });

        const longLivedUserToken = userTokenResponse.data.access_token;
        console.log('✅ Token de usuario de larga duración obtenido.');

        console.log('⏳ Paso 2: Obteniendo tokens de las páginas...');
        const pageTokenResponse = await axios.get('https://graph.facebook.com/v19.0/me/accounts', {
            params: {
                access_token: longLivedUserToken
            }
        });

        const pages = pageTokenResponse.data.data;
        const pageId = process.env.PAGE_ID;
        const targetPage = pages.find(p => p.id === pageId);

        if (targetPage) {
            console.log('\n🚀 ¡ÉXITO! Tu Long-Lived Page Token es:');
            console.log('--------------------------------------------------');
            console.log(targetPage.access_token);
            console.log('--------------------------------------------------');
            console.log('CÓPIALO Y ACTUALIZA TU SECRETO EN GITHUB (PAGE_ACCESS_TOKEN).');
        } else {
            console.log('❌ No se encontró la página con ID:', pageId);
            console.log('Páginas disponibles:', pages.map(p => `${p.name} (${p.id})`));
        }

    } catch (error) {
        console.error('❌ Error fatal:');
        if (error.response && error.response.data) {
            console.error(JSON.stringify(error.response.data, null, 2));
        } else {
            console.error(error.message);
        }
    }
}

getLongLivedToken();
