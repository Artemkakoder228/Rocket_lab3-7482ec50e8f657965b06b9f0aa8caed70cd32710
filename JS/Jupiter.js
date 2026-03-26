const tg = window.Telegram.WebApp;
tg.expand();

if (tg.initDataUnsafe.user) {
    const userElement = document.querySelector('.logo span');
    if(userElement) {
        userElement.innerText = `👨‍🚀 ${tg.initDataUnsafe.user.username.toUpperCase()}`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initHyperSpace();
    initInteractions();
    initNavigation();

    updateJupiterResources();
    setInterval(updateJupiterResources, 5000);
});

// --- 1. ФОНОВІ ЗІРКИ ---
function initHyperSpace() {
    const container = document.getElementById('space-container');
    if (!container) return;

    const starCount = 300;
    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        const x = Math.random() * 100;
        star.style.left = `${x}%`;

        const depth = Math.random();
        let size, duration;

        if (depth > 0.9) {
            size = Math.random() * 3 + 2;
            duration = Math.random() * 1 + 0.5;
            star.style.zIndex = "2";
        } else if (depth > 0.6) {
            size = Math.random() * 2 + 1;
            duration = Math.random() * 2 + 2;
            if(Math.random() > 0.8) star.classList.add('blue');
        } else {
            size = Math.random() * 1.5 + 0.5;
            duration = Math.random() * 5 + 5;
            star.style.opacity = Math.random() * 0.5 + 0.1;
            if(Math.random() > 0.9) star.classList.add('nebula');
        }

        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.animationDuration = `${duration}s`;
        star.style.animationDelay = `-${Math.random() * 10}s`;
        container.appendChild(star);
    }
}

// --- 2. ДАНІ МОДУЛІВ ---
const modulesData = {
    nose: { title: "Avionics Nose Cone", desc: "Aerodynamic cap housing main navigation computer and radar.", integrity: 98, level: 45 },
    cabin: { title: "Crew Command Deck", desc: "Pressurized module for 5 crew members. Radiation shielded.", integrity: 100, level: 60 },
    cargo: { title: "Secure Cargo Hold", desc: "Capacity: 15 Tons. Current payload: Rover Prototypes & Supplies.", integrity: 92, level: 30 },
    solar: { title: "Photovoltaic Array", desc: "Unfolds in orbit. Generates 50kW power for life support.", integrity: 88, level: 55 },
    body: { title: "Main Fuel Tank", desc: "Cryogenic Liquid Hydrogen/Oxygen storage. Thermal padding active.", integrity: 85, level: 40 },
    booster: { title: "Solid Rocket Booster", desc: "Provides 80% of lift-off thrust. Separation at altitude 50km.", integrity: 99, level: 25 },
    fins: { title: "Titanium Grid Fins", desc: "Hypersonic stabilization for atmospheric re-entry guiding.", integrity: 78, level: 35 },
    engine: { title: "Raptor-X Engine", desc: "Full flow staged combustion. Currently at 100% thrust output.", integrity: 94, level: 90 }
};

// --- 3. ВЗАЄМОДІЯ ---
function initInteractions() {
    const modules = document.querySelectorAll('.module');
    const panel = document.getElementById('infoPanel');
    const pTitle = document.getElementById('panelTitle');
    const pDesc = document.getElementById('panelDesc');
    const barIntegrity = document.getElementById('barIntegrity');
    const valIntegrity = document.getElementById('statIntegrity');
    const barLevel = document.getElementById('barLevel');
    const levelText = document.getElementById('statLevel');

    modules.forEach(mod => {
        mod.addEventListener('mouseenter', () => {
            const key = mod.getAttribute('data-module');
            const data = modulesData[key];
            if (!data) return;

            pTitle.innerText = data.title;
            pDesc.innerText = data.desc;
            barIntegrity.style.width = `${data.integrity}%`;
            valIntegrity.innerText = `${data.integrity}%`;
            if(data.integrity < 50) barIntegrity.style.background = 'red';
            else barIntegrity.style.background = 'var(--accent-cyan)';
            barLevel.style.width = `${data.level}%`;
            levelText.innerText = `MK-${Math.ceil(data.level/10)}`;
            panel.classList.add('active');
        });

        mod.addEventListener('click', () => {
            mod.style.filter = "brightness(2) drop-shadow(0 0 20px white)";
            setTimeout(() => { mod.style.filter = ""; }, 150);
        });
    });
}

// --- 4. НАВІГАЦІЯ (ВИПРАВЛЕНО) ---
function initNavigation() {
    const planets = document.querySelectorAll('.planet-item');
    planets.forEach(planet => {
        planet.addEventListener('click', () => {
            const planetName = planet.querySelector('.planet-name').innerText.trim();
            let targetPage = '';

            switch (planetName) {
                case 'EARTH': targetPage = 'index.html'; break;
                case 'MOON': targetPage = 'Moon.html'; break;
                case 'MARS': targetPage = 'Mars.html'; break;
                case 'JUPITER': targetPage = 'Jupiter.html'; break;
            }

            if (targetPage) {
                console.log(`Navigating to planet view: ${targetPage}`);
                // ВИКОРИСТОВУЄМО НОВУ ФУНКЦІЮ
                window.navigateTo(targetPage);
            }
        });
    });

    const treeBtn = document.querySelector('.tech-tree-btn');
    if (treeBtn) {
        treeBtn.addEventListener('click', () => {
            const activePlanet = document.querySelector('.planet-item.active');
            if (activePlanet) {
                const planetName = activePlanet.querySelector('.planet-name').innerText.trim();
                let treeFile = '';

                switch (planetName) {
                    case 'EARTH': treeFile = 'tree_Earth.html'; break;
                    case 'MOON': treeFile = 'tree_Moon.html'; break;
                    case 'MARS': treeFile = 'tree_Mars.html'; break;
                    case 'JUPITER': treeFile = 'tree_Jupiter.html'; break;
                }

                if (treeFile) {
                    console.log(`Navigating to tech tree: ${treeFile}`);
                    // ВИКОРИСТОВУЄМО НОВУ ФУНКЦІЮ
                    window.navigateTo(treeFile);
                }
            }
        });
    }

    const inventoryBtn = document.querySelector('.status-badge.inventory-sq');
    if (inventoryBtn) {
        inventoryBtn.addEventListener('click', () => {
             // ВИКОРИСТОВУЄМО НОВУ ФУНКЦІЮ
             window.navigateTo('inventory.html');
        });
    }
}

async function updateJupiterResources() {
    const urlParams = new URLSearchParams(window.location.search);
    const familyId = urlParams.get('family_id');
    if (!familyId) return;

    try {
        const response = await fetch(`/api/inventory?family_id=${familyId}`);
        if (!response.ok) return;

        const data = await response.json();
        if (data.resources) {
            const coinsEl = document.getElementById('val-coins');
            if (coinsEl) coinsEl.innerText = data.resources.coins;
            const hydEl = document.getElementById('val-hydrogen');
            if (hydEl) hydEl.innerText = data.resources.hydrogen;
            const helEl = document.getElementById('val-helium');
            if (helEl) helEl.innerText = data.resources.helium;
        }
    } catch (error) {
        console.error("Помилка отримання ресурсів:", error);
    }
}