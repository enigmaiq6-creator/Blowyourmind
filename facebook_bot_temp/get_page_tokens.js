const axios = require('axios');
require('dotenv').config();

const userToken = process.env.PAGE_ACCESS_TOKEN;
const pageId = process.env.PAGE_ID;

async function getPageTokens() {
    try {
        console.log(`--- Fetching Managed Pages for User ---`);
        const response = await axios.get(`https://graph.facebook.com/me/accounts`, {
            params: {
                access_token: userToken
            }
        });
        
        const accounts = response.data.data;
        if (!accounts || accounts.length === 0) {
            console.error('No se encontraron páginas vinculadas a este usuario.');
            return;
        }

        console.log(`Buscando Página ID: ${pageId}...`);
        const page = accounts.find(a => a.id === pageId);
        
        if (page) {
            console.log(`✅ ¡Encontrada! Página: ${page.name}`);
            console.log(`TOKEN_DE_PAGINA:${page.access_token}`);
        } else {
            console.log('❌ No se encontró la página especificada en la lista del usuario.');
            console.log('Páginas disponibles:');
            accounts.forEach(a => console.log(`- ${a.name} (ID: ${a.id})`));
        }
        
    } catch (error) {
        console.error('Error:', error.response ? error.response.data : error.message);
    }
}

getPageTokens();
