const fs = require('fs');
const path = require('path');
const mime = require('mime-types');
const { uploadPhoto, uploadVideo } = require('./facebookClient');

const CONTENT_DIR = './content';
const PROCESSED_DIR = './content/processed'; // Content moves here after upload

// Ensure directories exist
if (!fs.existsSync(CONTENT_DIR)) {
    fs.mkdirSync(CONTENT_DIR);
    console.log(`Created directory: ${CONTENT_DIR}`);
}
if (!fs.existsSync(PROCESSED_DIR)) {
    fs.mkdirSync(PROCESSED_DIR);
    console.log(`Created directory: ${PROCESSED_DIR}`);
}

async function processContent() {
    console.log('Scanning for content...');
    const files = fs.readdirSync(CONTENT_DIR);

    for (const file of files) {
        const filePath = path.join(CONTENT_DIR, file);

        // Skip directories and the processed folder itself
        if (fs.lstatSync(filePath).isDirectory()) continue;

        const mimeType = mime.lookup(filePath);
        if (!mimeType) {
            console.log(`Skipping unknown file type: ${file}`);
            continue;
        }

        try {
            if (mimeType.startsWith('image/')) {
                await uploadPhoto(filePath, `Posted via Automator: ${file}`);
            } else if (mimeType.startsWith('video/')) {
                await uploadVideo(filePath, `Posted via Automator: ${file}`);
            } else {
                console.log(`Skipping unsupported file type: ${file} (${mimeType})`);
                continue;
            }

            // Move to processed folder
            const destination = path.join(PROCESSED_DIR, file);
            fs.renameSync(filePath, destination);
            console.log(`Moved ${file} to processed folder.`);

        } catch (error) {
            console.error(`Failed to process ${file}. Leaving in content folder.`);
        }
    }
    console.log('Content processing complete.');
}

processContent().catch(console.error);
