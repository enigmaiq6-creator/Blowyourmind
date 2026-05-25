const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

function getDriveClient() {
    let credentials;
    const credsPath = path.join(__dirname, 'google_creds.json');

    if (fs.existsSync(credsPath)) {
        try {
            credentials = JSON.parse(fs.readFileSync(credsPath, 'utf8'));
            if (credentials.private_key) {
                credentials.private_key = credentials.private_key.replace(/\\n/g, '\n');
            }
            console.log('✅ Cargadas credenciales desde google_creds.json');
        } catch (e) {
            console.error('Error leyendo google_creds.json', e);
        }
    }

    if (!credentials && process.env.GOOGLE_CREDENTIALS) {
        try {
            credentials = JSON.parse(process.env.GOOGLE_CREDENTIALS);
            if (credentials.private_key) {
                credentials.private_key = credentials.private_key.replace(/\\n/g, '\n');
            }
            console.log('✅ Cargadas credenciales desde variables de entorno');
        } catch (e) {
            console.error('Error parseando GOOGLE_CREDENTIALS', e);
        }
    }

    if (!credentials) {
        throw new Error('No se encontraron credenciales de Google (archivo o env).');
    }

    const auth = new google.auth.GoogleAuth({
        credentials,
        scopes: ['https://www.googleapis.com/auth/drive']
    });

    return google.drive({ version: 'v3', auth });
}

async function getFirstVideo(pendingFolderId) {
    const drive = getDriveClient();
    console.log(`Buscando videos en la carpeta ${pendingFolderId}...`);
    
    // Buscar archivos (solo videos si queremos ser estrictos)
    const res = await drive.files.list({
        q: `'${pendingFolderId}' in parents and trashed=false and mimeType contains 'video/'`,
        fields: 'files(id, name, mimeType)',
        spaces: 'drive',
        pageSize: 1
    });

    if (res.data.files && res.data.files.length > 0) {
        return res.data.files[0];
    } else {
        return null;
    }
}

async function downloadVideo(fileId, destPath) {
    const drive = getDriveClient();
    console.log(`Descargando archivo ${fileId} a ${destPath}...`);

    return new Promise(async (resolve, reject) => {
        try {
            const dest = fs.createWriteStream(destPath);
            const res = await drive.files.get(
                { fileId, alt: 'media' },
                { responseType: 'stream' }
            );

            res.data
                .on('end', () => {
                    console.log('Descarga completada.');
                    resolve(destPath);
                })
                .on('error', err => {
                    console.error('Error al descargar:', err);
                    reject(err);
                })
                .pipe(dest);
        } catch (err) {
            console.error('Error llamando a la API de Drive:', err);
            reject(err);
        }
    });
}

async function moveFile(fileId, previousFolderId, newFolderId) {
    const drive = getDriveClient();
    console.log(`Moviendo archivo ${fileId} a ${newFolderId}...`);
    
    // Para mover el archivo, lo agregamos a la nueva carpeta y lo quitamos de la anterior
    await drive.files.update({
        fileId: fileId,
        addParents: newFolderId,
        removeParents: previousFolderId,
        fields: 'id, parents'
    });
    
    console.log(`Archivo movido con éxito.`);
}

module.exports = {
    getFirstVideo,
    downloadVideo,
    moveFile
};
