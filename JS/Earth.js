const tg = window.Telegram.WebApp;
tg.expand();

// Відображення імені користувача
if (tg.initDataUnsafe.user) {
    const userElement = document.querySelector('.logo span'); 
    if(userElement) {
        userElement.innerText = `👨‍🚀 ${tg.initDataUnsafe.user.username.toUpperCase()}`;
    }
}

// --- 1. НАЛАШТУВАННЯ СТАРТОВОГО СТАНУ (ДЕФОЛТ) ---
const defaultRocketState = {
    nose: 1, body: 1, engine: 1, fins: 1,
    cabin: 0, cargo: 0, solar: 0, booster: 0
};

// --- 2. ФУНКЦІЯ ЗАВАНТАЖЕННЯ ---
function loadRocketState() {
    const savedData = localStorage.getItem('myRocketSave');
    if (savedData) {
        return JSON.parse(savedData);
    } else {
        return JSON.parse(JSON.stringify(defaultRocketState));
    }
}

let rocketState = loadRocketState();
let selectedModuleKey = null;

document.addEventListener("DOMContentLoaded", () => {
    console.log('🚀 Rocket Lab Loading...');
    console.log('📦 Loaded State:', rocketState);

    initHyperSpace();
    updateRocketVisuals();
    initInteractions();
    initNavigation();

    // Запуск оновлення ресурсів
    updateEarthResources();
    setInterval(updateEarthResources, 5000);

    console.log('✅ Rocket Lab Ready!');
});

// --- 3. ОНОВЛЕННЯ ГРАФІКИ ---
function updateRocketVisuals() {
    for (const [key, level] of Object.entries(rocketState)) {
        const elements = document.querySelectorAll(`[data-module="${key}"]`);
        elements.forEach(el => {
            el.classList.remove('tier-0', 'tier-1', 'tier-2');
            if (level > 0) {
                el.classList.add(`tier-${level}`);
                el.style.display = '';
                if (window.getComputedStyle(el).display === 'none') {
                     el.style.display = 'block';
                }
            } else {
                el.style.display = 'none';
            }
        });
    }
}

// --- ЛОГІКА АПГРЕЙДУ ---
function upgradeSelectedModule() {
    if (!selectedModuleKey) return;
    if (rocketState[selectedModuleKey] === 0) {
        alert("Цей модуль ще не встановлено! Перейдіть у Дерево Розробок.");
        return;
    }

    const currentLevel = rocketState[selectedModuleKey];
    const btn = document.querySelector('.upgrade-btn');

    if (currentLevel < 2) {
        btn.innerText = "INSTALLING...";
        setTimeout(() => {
            rocketState[selectedModuleKey]++;
            localStorage.setItem('myRocketSave', JSON.stringify(rocketState));
            updateRocketVisuals();
            refreshInfoPanel(selectedModuleKey);
            btn.innerText = "COMPLETE!";
            setTimeout(() => {
                updateButtonState(rocketState[selectedModuleKey]);
            }, 1000);
        }, 500);
    }
}

function updateButtonState(level) {
    const btn = document.querySelector('.upgrade-btn');
    if (level === 0) {
        btn.innerText = "LOCKED (RESEARCH NEEDED)";
        btn.style.background = "#333";
        btn.style.color = "#888";
    } else if (level === 1) {
        btn.innerText = "UPGRADE TO MK-2 (5000 $)";
        btn.style.background = "rgba(0, 243, 255, 0.1)";
        btn.style.color = "var(--accent-cyan)";
        btn.disabled = false;
    } else {
        btn.innerText = "MAX LEVEL";
        btn.style.background = "var(--accent-green)";
        btn.style.color = "black";
        btn.disabled = true;
    }
}

function initInteractions() {
    const modules = document.querySelectorAll('.module');
    const panel = document.getElementById('infoPanel');
    const upgradeBtn = document.querySelector('.upgrade-btn');

    if(upgradeBtn) {
        upgradeBtn.addEventListener('click', upgradeSelectedModule);
    }

    modules.forEach(mod => {
        mod.addEventListener('mouseenter', () => {
            const key = mod.getAttribute('data-module');
            selectedModuleKey = key;
            refreshInfoPanel(key);
            panel.classList.add('active');
        });
        mod.addEventListener('click', () => {
             selectedModuleKey = mod.getAttribute('data-module');
             refreshInfoPanel(selectedModuleKey);
        });
    });
}

function refreshInfoPanel(key) {
    const currentLevel = rocketState[key] || 0;
    const nodes = window.treeNodes || [];
    const activeNode = nodes.find(n => n.rocketKey === key && n.level === currentLevel);
    const nextNode = nodes.find(n => n.rocketKey === key && n.level === currentLevel + 1);

    const pTitle = document.getElementById('panelTitle');
    const pDesc = document.getElementById('panelDesc');
    const btn = document.querySelector('.upgrade-btn');

    if (activeNode) {
        pTitle.innerText = activeNode.name.toUpperCase();
        pDesc.innerText = activeNode.desc;
        if (nextNode) {
            const cost = nextNode.cost;
            btn.innerText = `UPGRADE: ${cost.iron}🔩 | ${cost.coins}🪙`;
            btn.style.display = 'block';
            btn.disabled = false;
        } else {
            btn.innerText = "MAX LEVEL REACHED";
            btn.disabled = true;
            btn.style.background = "var(--accent-green)";
        }
    } else {
        pTitle.innerText = "LOCKED MODULE";
        pDesc.innerText = "Дослідіть цей модуль у дереві розробок.";
        btn.innerText = "GO TO TECH TREE";
    }

    const levelPercent = (currentLevel / 2) * 100;
    document.getElementById('barLevel').style.width = `${levelPercent}%`;
    document.getElementById('statLevel').innerText = `MK-${currentLevel}`;
}

// --- НАВІГАЦІЯ (ВИПРАВЛЕНО) ---
function initNavigation() {
    // 1. Кнопки планет
    const planets = document.querySelectorAll('.planet-item');

    planets.forEach(planet => {
        planet.addEventListener('click', () => {
            const nameElement = planet.querySelector('.planet-name');
            if (!nameElement) return;

            const name = nameElement.innerText.trim();
            let targetPage = '';

            switch (name) {
                case 'EARTH': targetPage = 'index.html'; break;
                case 'MOON':  targetPage = 'Moon.html'; break;
                case 'MARS':  targetPage = 'Mars.html'; break;
                case 'JUPITER': targetPage = 'Jupiter.html'; break;
            }

            if (targetPage) {
                console.log(`Navigating to: ${targetPage}`);
                // ВИКОРИСТОВУЄМО НОВУ ФУНКЦІЮ
                window.navigateTo(targetPage);
            }
        });
    });

    // 2. Кнопка Дерева Розробок
    const treeBtn = document.querySelector('.tech-tree-btn');
    if (treeBtn) {
        treeBtn.addEventListener('click', () => {
            const activePlanet = document.querySelector('.planet-item.active');
            let treeFile = 'tree_Earth.html';

            if (activePlanet) {
                const planetName = activePlanet.querySelector('.planet-name').innerText.trim();
                if (planetName === 'MOON') treeFile = 'tree_Moon.html';
                else if (planetName === 'MARS') treeFile = 'tree_Mars.html';
                else if (planetName === 'JUPITER') treeFile = 'tree_Jupiter.html';
            }
            // ВИКОРИСТОВУЄМО НОВУ ФУНКЦІЮ
            window.navigateTo(treeFile);
        });
    }

    // 3. Кнопка Інвентарю
    const inventoryBtn = document.querySelector('.status-badge.inventory-sq');
    if (inventoryBtn) {
        inventoryBtn.addEventListener('click', () => {
            // ВИКОРИСТОВУЄМО НОВУ ФУНКЦІЮ (вона сама додасть ID)
            window.navigateTo('inventory.html');
        });
    }
}

// --- ФОНОВІ ЗІРКИ ---
function initHyperSpace() {
    const container = document.getElementById('space-container');
    if (!container) return;
    container.innerHTML = '';
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
            if (Math.random() > 0.8) star.classList.add('blue');
        } else {
            size = Math.random() * 1.5 + 0.5;
            duration = Math.random() * 5 + 5;
            star.style.opacity = Math.random() * 0.5 + 0.1;
            if (Math.random() > 0.9) star.classList.add('nebula');
        }

        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.animationDuration = `${duration}s`;
        star.style.animationDelay = `-${Math.random() * 10}s`;
        container.appendChild(star);
    }
}

// --- ДАНІ МОДУЛІВ ---
const modulesData = {
    nose: { title: "Nose Cone", desc: "Aerodynamic cap.", integrity: 98, level: 10 },
    cabin: { title: "Crew Deck", desc: "Pressurized module.", integrity: 100, level: 60 },
    cargo: { title: "Cargo Hold", desc: "Capacity: 15 Tons.", integrity: 92, level: 30 },
    solar: { title: "Solar Array", desc: "Generates power.", integrity: 88, level: 55 },
    body: { title: "Fuel Tank", desc: "Liquid Hydrogen.", integrity: 85, level: 40 },
    booster: { title: "Solid Booster", desc: "Lift-off thrust.", integrity: 99, level: 25 },
    fins: { title: "Grid Fins", desc: "Stabilization.", integrity: 78, level: 35 },
    engine: { title: "Raptor Engine", desc: "Main propulsion.", integrity: 94, level: 90 }
};

async function updateEarthResources() {
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

            const ironEl = document.getElementById('val-iron');
            if (ironEl) ironEl.innerText = data.resources.iron;

            const fuelEl = document.getElementById('val-fuel');
            if (fuelEl) fuelEl.innerText = data.resources.fuel;
        }
    } catch (error) {
        console.error("Помилка отримання ресурсів:", error);
    }
}