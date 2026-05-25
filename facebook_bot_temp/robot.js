const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
require('dotenv').config();

// Configuration
const TARGET_PAGE_NAME = "Enigmaiq";
const CONTENT_DIR = './content';
const PROCESSED_DIR = './content/processed';
const USER_DATA_DIR = './user_data_new';

// Helper to wait
const delay = (time) => new Promise(resolve => setTimeout(resolve, time));

// --- 🧠 CREATIVE ENGINE (Generates Descriptions) ---
function generateDescription(filename) {
    // Clean filename: "super_video_viral.mp4" -> "super video viral"
    const title = filename.replace(/[-_]/g, ' ').replace(/\s+/g, ' ').trim();

    // Arrays for mixing content
    const intros = [
        "¡Hola a todos! 👋 Hoy les traigo algo especial.",
        "✨ ¡Nuevo video en la página!",
        "¡No se pueden perder esto! 😱",
        "📢 Atención a este nuevo contenido.",
        "¡Miren lo que preparé para ustedes hoy! 🔥"
    ];

    const middles = [
        `El tema de hoy es: ${title}.`,
        `En este video veremos todo sobre: ${title}.`,
        `Disfruten de ${title}, sé que les va a encantar.`,
        `Aquí les comparto ${title}. ¡Está increíble!`
    ];

    const outros = [
        "¡Espero que les guste tanto como a mí! 👍",
        "Déjenme saber qué opinan en los comentarios. 👇",
        "¡Dale LIKE y COMPARTE si te gustó! ❤️",
        "¡Gracias por el apoyo de siempre! 🙏"
    ];

    // Generate hashtags based on title words
    const commonTags = ["#Enigmaiq", "#VideoViral", "#Contenido", "#ParaTi"];
    const titleTags = title.split(' ')
        .filter(w => w.length > 3) // Only words longer than 3 chars
        .map(w => `#${w.charAt(0).toUpperCase() + w.slice(1)}`)
        .slice(0, 3); // Take up to 3 tags from title

    const allTags = [...new Set([...commonTags, ...titleTags])].join(' ');

    // Pick random elements
    const random = (arr) => arr[Math.floor(Math.random() * arr.length)];

    return `${random(intros)}\n\n${random(middles)}\n\n${random(outros)}\n\n${allTags}`;
}

(async () => {
    console.log('🤖 Starting Facebook Robot...');

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null, // Maximized
        args: ['--start-maximized', '--disable-notifications'],
        userDataDir: USER_DATA_DIR
    });

    const page = await browser.newPage();

    try {
        console.log('Navigating to Facebook...');
        await page.goto('https://www.facebook.com', { waitUntil: 'networkidle2' });

        // Login Check
        const isLoggedIn = await page.$('div[aria-label="Account controls and settings"], div[aria-label="Controles y configuración de la cuenta"]');
        if (!isLoggedIn) {
            console.log('⚠️  NOT LOGGED IN. Waiting for manual login...');
            await page.waitForSelector('div[aria-label="Account controls and settings"], div[aria-label="Controles y configuración de la cuenta"]', { timeout: 0 });
            console.log('✅ Login detected!');
            await delay(3000);
        } else {
            console.log('✅ Already logged in.');
        }

        console.log('⏳ Waiting 10 seconds for you to ensure you are on the Page Profile...');
        await delay(10000);

        // Process Content
        console.log('📂 Scanning content folder...');
        if (!fs.existsSync(CONTENT_DIR)) fs.mkdirSync(CONTENT_DIR);
        if (!fs.existsSync(PROCESSED_DIR)) fs.mkdirSync(PROCESSED_DIR);

        const files = fs.readdirSync(CONTENT_DIR);

        for (const file of files) {
            if (fs.lstatSync(path.join(CONTENT_DIR, file)).isDirectory()) continue;
            if (file === 'processed') continue;
            if (!file.match(/\.(mp4|mov|avi|jpg|jpeg|png)$/i)) continue;

            const filePath = path.join(process.cwd(), CONTENT_DIR, file);
            const fileNameWithoutExt = path.parse(file).name;

            // Prioritize manual txt file, otherwise generate one
            let description;
            const descPath = path.join(CONTENT_DIR, `${fileNameWithoutExt}.txt`);

            if (fs.existsSync(descPath)) {
                description = fs.readFileSync(descPath, 'utf8');
                console.log(`📝 Found manual description for ${file}`);
            } else {
                description = generateDescription(fileNameWithoutExt);
                console.log(`🧠 Generated smart description for ${file}`);
            }

            console.log(`🚀 Uploading: ${file}`);

            try {
                await uploadPost(page, filePath, description);

                // Move to processed
                fs.renameSync(path.join(CONTENT_DIR, file), path.join(PROCESSED_DIR, file));
                if (fs.existsSync(descPath)) {
                    fs.renameSync(descPath, path.join(PROCESSED_DIR, `${fileNameWithoutExt}.txt`));
                }
                console.log(`✅ Finished ${file}. Moved to processed.`);
                console.log('⏳ Waiting 30 seconds before next upload...');
                await delay(30000);

            } catch (e) {
                console.error(`❌ Failed to upload ${file}:`, e);
                fs.appendFileSync('error_log.txt', `Failed ${file}: ${e.message}\n`);
            }
        }

    } catch (error) {
        console.error("FATAL ERROR:", error);
        fs.writeFileSync('fatal_error.txt', String(error));
    } finally {
        console.log('🎉 Script finished.');
    }
})();

async function uploadPost(page, filePath, description) {
    console.log("Looking for 'Photo/video' button...");

    // 1. Try to find File Input directly
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
        console.log("Found file input directly. Uploading...");
        await fileInput.uploadFile(filePath);
    } else {
        console.log("File input not found. Clicking buttons...");

        // Ensure composer is open
        const composer = await page.$('div[role="button"] span');
        if (composer) {
            const text = await page.evaluate(el => el.textContent, composer);
            if (text.match(/mind|pensando|tú|you/i)) {
                await composer.click();
                await delay(2000);
            }
        }

        const [fileChooser] = await Promise.all([
            page.waitForFileChooser({ timeout: 5000 }).catch(() => null),
            page.evaluate(() => {
                const nodes = Array.from(document.querySelectorAll('div[aria-label], span'));
                const target = nodes.find(n => {
                    const txt = n.textContent || n.getAttribute('aria-label') || '';
                    return txt.match(/Foto|Photo|Video/i);
                });
                if (target) {
                    target.click();
                    return true;
                }
                return false;
            })
        ]);

        if (fileChooser) {
            await fileChooser.accept([filePath]);
        } else {
            const input2 = await page.$('input[type="file"]');
            if (input2) {
                await input2.uploadFile(filePath);
            } else {
                throw new Error("Could not find file upload input.");
            }
        }
    }

    console.log('⏳ Waiting 20 seconds for upload processing...');
    await delay(20000); // Increased wait time

    // 2. Enter Description
    console.log('✍️ Writing description...');
    const textBox = await page.$('div[role="textbox"][aria-label*="ublic"]');

    if (textBox) {
        await textBox.click();
        await page.keyboard.type(description);
    } else {
        const genericBox = await page.$('div[role="textbox"]');
        if (genericBox) {
            await genericBox.click();
            await page.keyboard.type(description);
        }
    }
    await delay(3000);

    // 3. Click Post (With Retry)
    console.log('Publishing...');

    let posted = false;
    for (let i = 0; i < 30; i++) { // Retry 30 times (approx 5 mins max wait)
        const postButton = await page.evaluateHandle(() => {
            const buttons = Array.from(document.querySelectorAll('div[role="button"]'));
            return buttons.find(b => {
                const txt = b.innerText || b.getAttribute('aria-label') || '';
                return txt.match(/^(Publicar|Post)$/i) && b.getAttribute('aria-disabled') !== 'true';
            });
        });

        if (postButton && postButton.asElement()) {
            console.log('Clicking Post button...');
            await postButton.click();
            posted = true;
            break;
        }

        console.log(`[Attempt ${i + 1}/30] Post button not ready. Waiting 10s...`);
        await delay(10000);
    }

    if (!posted) {
        throw new Error("Could not find enabled Post button after multiple attempts.");
    }

    console.log('⏳ Waiting 60 seconds for post to finalize...');
    await delay(60000);
}
