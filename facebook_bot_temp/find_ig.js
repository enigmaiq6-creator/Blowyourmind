const axios = require('axios');
require('dotenv').config();

const token = process.env.PAGE_ACCESS_TOKEN;
const pageId = process.env.PAGE_ID;

async function findIG() {
    try {
        console.log(`--- Finding Instagram Account for Page: ${pageId} ---`);
        const response = await axios.get(`https://graph.facebook.com/v20.0/${pageId}`, {
            params: {
                fields: 'instagram_business_account,name',
                access_token: token
            }
        });
        
        console.log('✅ Respuesta de la Página:');
        console.log(JSON.stringify(response.data, null, 2));

        if (response.data.instagram_business_account) {
            console.log(`\n¡ENCONTRADO! El ID de Instagram vinculado es: ${response.data.instagram_business_account.id}`);
        } else {
            console.log('\n❌ La página no reporta ninguna cuenta de Instagram vinculada con este token.');
        }

    } catch (error) {
        console.error('❌ Error:', error.response ? error.response.data : error.message);
    }
}

findIG();
