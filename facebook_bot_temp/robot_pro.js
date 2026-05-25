const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
require('dotenv').config();

// --- CONFIGURATION ---
const CONTENT_DIR = './content';
const PROCESSED_DIR = './content/processed';
const USER_DATA_DIR = './user_data_new'; // Reuse successful profile
const SCHEDULE_TIMES = [13, 18]; // 1 PM and 6 PM
const MEMORY_FILE = './schedule_memory.json'; // To remember last scheduled slot

// --- HELPERS ---
const delay = (time) => new Promise(resolve => setTimeout(resolve, time));

// Persistent Scheduler Memory
function getLastScheduleDate() {
    if (fs.existsSync(MEMORY_FILE)) {
        try {
            const data = JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
            const lastDate = new Date(data.lastDate);
            if (lastDate > new Date()) {
                return lastDate;
            }
        } catch (e) {
            console.log('⚠️ Could not read memory file, starting fresh.');
        }
    }
    return new Date(); // Default to Now
}

function saveScheduleDate(date) {
    fs.writeFileSync(MEMORY_FILE, JSON.stringify({ lastDate: date }));
}

// Generate Description (Reuse Creative Engine)
function generateDescription(filename) {
    const title = filename.replace(/[-_]/g, ' ').replace(/\s+/g, ' ').trim();
    const headers = [
        "¡Nuevo contenido para ustedes! ✨",
        "No se pierdan esto 👇",
        "Disfruten de este video 🎥",
        "Aquí les dejo algo especial 🔥"
    ];
    const footers = [
        "#Enigmaiq #Viral #Contenido",
        "#Colombia #FYP #Reels",
        "#VideoDelDia #Siguenos"
    ];
    const random = arr => arr[Math.floor(Math.random() * arr.length)];
    return `${random(headers)}\n\n${title}\n\n${random(footers)}`;
}

// Date Scheduler Generator
function getNextSlots(count) {
    let slots = [];
    let date = getLastScheduleDate(); // Start from memory or now

    // Safety buffer: If starting from NOW, add 30 mins. 
    if (new Date() - date < 60000) {
        date.setMinutes(date.getMinutes() + 30);
    } else {
        date.setMinutes(date.getMinutes() + 1);
    }

    // Generate enough slots for all files
    while (slots.length < count) {
        for (let hour of SCHEDULE_TIMES) {
            let slot = new Date(date);
            slot.setHours(hour, 0, 0, 0);

            if (slot > date) {
                slots.push(slot);
                if (slots.length >= count) break;
            }
        }
        date.setDate(date.getDate() + 1);
        date.setHours(0, 0, 0, 0);
    }
    return slots;
}

function formatDateForFacebook(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

function formatTimeForFacebook(date) {
    let hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    return `${hours}:${minutes} ${ampm}`;
}

// --- MAIN ROBOT LOGIC ---
(async () => {
    console.log('🤖 STARTING ROBOT PRO (SCHEDULER VERSION)...');
    console.log('🎯 Target: Meta Business Suite');

    // 1. Prepare Content
    if (!fs.existsSync(CONTENT_DIR)) fs.mkdirSync(CONTENT_DIR);
    if (!fs.existsSync(PROCESSED_DIR)) fs.mkdirSync(PROCESSED_DIR);

    const files = fs.readdirSync(CONTENT_DIR)
        .filter(f => f.match(/\.(mp4|mov|avi|jpg|png|jpeg)$/i))
        .filter(f => fs.lstatSync(path.join(CONTENT_DIR, f)).isFile());

    if (files.length === 0) {
        console.log('❌ No files found in content folder!');
        return;
    }

    console.log(`📅 Found ${files.length} files to schedule.`);
    const slots = getNextSlots(files.length);
    console.log(`🕒 Schedule Preview:\n  First: ${slots[0].toLocaleString()}\n  Last: ${slots[slots.length - 1].toLocaleString()}`);

    // 2. Launch Browser
    const browser = await puppeteer.launch({
        headless: false,
        args: ['--start-maximized', '--disable-notifications'],
        userDataDir: USER_DATA_DIR
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1366, height: 768 });

    // 3. Process Loop
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const slot = slots[i];
        const filePath = path.join(process.cwd(), CONTENT_DIR, file);
        const isVideo = file.match(/\.(mp4|mov|avi)$/i);

        console.log(`\n🎬 Processing [${i + 1}/${files.length}]: ${file}`);
        console.log(`⏰ Scheduled for: ${slot.toLocaleString()}`);

        try {
            // Navigate to Business Suite Composer
            await page.goto('https://business.facebook.com/latest/composer', { waitUntil: 'networkidle2' });
            await delay(10000); // Increased wait for full heavy load

            // 0. NEW: DISMISS BLOCKING POPUPS
            console.log('🔍 Checking for blocking popups...');
            await page.evaluate(() => {
                // Find buttons with text "Listo", "Done", "Entendido"
                const commonDismissTexts = ['listo', 'done', 'entendido', 'ok', 'aceptar'];
                const buttons = Array.from(document.querySelectorAll('div[role="button"], span, div'));
                const dismissBtn = buttons.find(el => {
                    const txt = el.innerText?.toLowerCase().trim() || '';
                    return commonDismissTexts.includes(txt);
                });
                
                if (dismissBtn) {
                    console.log('Closing popup with button:', dismissBtn.innerText);
                    dismissBtn.click();
                }

                // Also try to find close icons (X)
                const closeIcons = Array.from(document.querySelectorAll('i, svg, div[aria-label="Cerrar"], div[aria-label="Close"]'));
                const closeBtn = closeIcons.find(el => {
                    const label = el.getAttribute('aria-label')?.toLowerCase() || '';
                    return label === 'cerrar' || label === 'close';
                });
                if (closeBtn) closeBtn.click();
            });
            await delay(3000);

            // A. UPLOAD TYPE SELECTION
            if (isVideo) {
                console.log('Selecting REEL format...');
                const reelBtn = await page.evaluateHandle(() => {
                    return Array.from(document.querySelectorAll('div, span, button'))
                        .find(el => {
                            const txt = el.innerText?.toLowerCase() || '';
                            // Match 'reel', 'reels', 'crear reel', etc.
                            return txt === 'reel' || txt === 'reels' || txt === 'crear reel' || (txt.includes('reel') && txt.length < 20);
                        });
                });
                if (reelBtn.asElement()) {
                    await reelBtn.click();
                    await delay(3000);
                } else {
                    console.log('⚠️ Warning: "Reel" button not found. Defaults might apply.');
                }
            } else {
                console.log('Selecting POST format...');
            }

            // B. UPLOAD
            console.log('Uploading file...');

            // 1. Try finding "Add Video"/"Agregar video" button
            const addMediaBtn = await page.evaluateHandle(() => {
                const keywords = [
                    'add video', 'agregar video', 'subir video', 'video',
                    'add photo', 'agregar foto', 'foto', 'agregar foto/video'
                ];
                // Priority to buttons with specific text
                const elements = Array.from(document.querySelectorAll('div[role="button"], span, div, button'));
                return elements.find(el => {
                    const txt = el.innerText?.toLowerCase().trim() || '';
                    // Precise match or contains
                    return keywords.some(k => txt === k || (txt.includes(k) && txt.length < 30));
                });
            });

            if (addMediaBtn.asElement()) {
                console.log('Found "Add Media" button, clicking...');
                await addMediaBtn.click();
                await delay(2000);

                // Check if submenu "Upload from desktop" appears
                const uploadDesktop = await page.evaluateHandle(() => {
                    return Array.from(document.querySelectorAll('span, div'))
                        .find(el => {
                            const txt = el.innerText?.toLowerCase() || '';
                            return txt.includes('desktop') || txt.includes('computadora') || txt.includes('ordenador');
                        });
                });
                if (uploadDesktop.asElement()) {
                    await uploadDesktop.click();
                    await delay(1000);
                }
            } else {
                console.log('⚠️ Could not find explicit "Add Video" button. Trying fallback input...');
            }

            // 2. Upload via File Input (Hidden or visible)
            // Force hidden inputs to be active if needed, or just find any file input
            const fileInput = await page.$('input[type="file"]');
            if (fileInput) {
                await fileInput.uploadFile(filePath);
            } else {
                // Try file chooser trigger if clicked button opened system dialog
                const fileChooser = await page.waitForFileChooser({ timeout: 2000 }).catch(() => null);
                if (fileChooser) {
                    await fileChooser.accept([filePath]);
                } else {
                    throw new Error("Could not find upload input or trigger file chooser!");
                }
            }

            // C. WAIT FOR 100%
            console.log('⏳ Waiting for upload to complete (100%)...');
            await page.waitForFunction(() => {
                const body = document.body.innerText;
                // English, Spanish, Portuguese checkmarks
                return body.includes('100%') || body.includes('Subida completa') || body.includes('Upload complete') || body.includes('Completo');
            }, { timeout: 600000 }); // Wait up to 10 mins
            console.log('✅ Upload Complete!');
            await delay(3000);

            // D. DESCRIPTION
            let desc = generateDescription(file);
            const descPath = path.join(CONTENT_DIR, `${path.parse(file).name}.txt`);
            if (fs.existsSync(descPath)) desc = fs.readFileSync(descPath, 'utf8');

            console.log('✍️ Adding description...');
            await page.evaluate((text) => {
                // Look for DraftJS editor or generic textbox
                const editor = document.querySelector('[role="textbox"], [contenteditable="true"]');
                if (editor) {
                    editor.focus();
                    document.execCommand('insertText', false, text);
                }
            }, desc);
            await delay(2000);

            // E. NEXT / SCHEDULE
            console.log('➡️ Moving to Schedule...');

            // Loop Next button until Schedule option appears
            for (let j = 0; j < 5; j++) {
                // Try clicking Next/Siguiente
                const nextBtn = await page.evaluateHandle(() => {
                    return Array.from(document.querySelectorAll('div[role="button"], span'))
                        .find(el => {
                            const txt = el.innerText?.toLowerCase() || '';
                            return txt === 'next' || txt === 'siguiente';
                        });
                });

                if (nextBtn.asElement()) {
                    // Check if it's clickable (not disabled)
                    await nextBtn.click();
                    await delay(2000);
                }

                // Check if Schedule option is visible
                const scheduleRadio = await page.evaluateHandle(() => {
                    return Array.from(document.querySelectorAll('span, label'))
                        .find(el => {
                            const txt = el.innerText?.toLowerCase() || '';
                            return txt.includes('schedule') || txt.includes('programar');
                        });
                });

                if (scheduleRadio.asElement()) {
                    await scheduleRadio.click();
                    console.log('Select "Schedule" option.');
                    break;
                }
            }

            // F. INPUT DATE/TIME
            console.log(`📅 Setting date: ${formatDateForFacebook(slot)} ${formatTimeForFacebook(slot)}`);

            // This part is manual-assist usually because date pickers are notoriously complex.
            // We click the Schedule/Programar button to FINALIZE.

            const submitBtn = await page.evaluateHandle(() => {
                return Array.from(document.querySelectorAll('div[role="button"]'))
                    .find(el => {
                        const txt = el.innerText?.toLowerCase() || '';
                        return (txt === 'schedule' || txt === 'programar') && !el.getAttribute('aria-disabled');
                    });
            });

            if (submitBtn.asElement()) {
                await submitBtn.click();
                console.log('🎉 Scheduled successfully!');
            } else {
                throw new Error("Could not find final Schedule button");
            }

            // G. CLEANUP & SAVE
            await delay(5000);

            fs.renameSync(path.join(CONTENT_DIR, file), path.join(PROCESSED_DIR, file));
            if (fs.existsSync(descPath)) fs.renameSync(descPath, path.join(PROCESSED_DIR, `${path.parse(file).name}.txt`));

            saveScheduleDate(slot);
            console.log('✅ File processed & moved.');
            await delay(5000);

        } catch (e) {
            console.error(`❌ Error processing ${file}:`, e);
            console.log('⚠️ Skipping to next file...');
            fs.appendFileSync('error_log_pro.txt', `${file} - ${e.message}\n`);
            try { await page.screenshot({ path: `error_${file}.png` }); } catch (err) { }
        }
    }

    console.log('🏁 Batch finished.');
})();
