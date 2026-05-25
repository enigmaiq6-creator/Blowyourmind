const axios = require('axios');
require('dotenv').config();

const token = process.env.PAGE_ACCESS_TOKEN;

async function debug() {
    try {
        console.log('\n--- Checking Permissions (me/permissions) ---');
        const perms = await axios.get(`https://graph.facebook.com/me/permissions`, {
            params: { access_token: token }
        });
        console.log(JSON.stringify(perms.data, null, 2));

        console.log('\n--- Checking User/Page Info (me) ---');
        const me = await axios.get(`https://graph.facebook.com/me`, {
            params: { fields: 'id,name', access_token: token }
        });
        console.log(JSON.stringify(me.data, null, 2));

    } catch (error) {
        console.error('Error:', error.response ? error.response.data : error.message);
    }
}

debug();
