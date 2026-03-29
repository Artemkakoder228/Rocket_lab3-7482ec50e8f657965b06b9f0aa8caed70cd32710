const tg = window.Telegram.WebApp;
tg.expand();

// Відображення імені
if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
    const userElement = document.querySelector('.logo span'); 
    if(userElement) {
        userElement.innerText = `👨‍🚀 ${tg.initDataUnsafe.user.username.toUpperCase()}`;
    }
}

let selectedModuleKey = null;
let userOwnedModules = []; 

// === ТОЧНІ ID МОДУЛІВ ===
const PLANET_MODULE_POOLS = {
    'EARTH': ['gu1', 'gu2', 'nc1', 'h1', 'e1', 'e2', 'a1', 'a2'],
    'MOON':  ['root1', 'branch1_up1', 'branch1_up2', 'branch1_down1', 'root2', 'branch2_up', 'branch2_down', 'root3', 'branch3'],
    // ДОДАЛИ g1_up2 ТА g2_down2 СЮДИ:
    'MARS':  ['g1_1', 'g1_2', 'g1_up', 'g1_up2', 'g1_down', 'g1_end', 'g2_1', 'g2_up', 'g2_down', 'g2_down2', 'g3_a1', 'g3_a2', 'g3_b1', 'g3_b2'],
    'JUPITER': ['hull_start', 'hull_mk2', 'solar_upg', 'solar_max', 'aux_bay', 'combat_bay', 'cannons', 'eng_start', 'eng_ultimate', 'eng_side', 'nose_start', 'nose_adv']
};

document.addEventListener("DOMContentLoaded", () => {
    initHyperSpace();
    initInteractions(); 
    initNavigation();

    // Запускаємо оновлення ресурсів
    updateMarsResources();
    setInterval(updateMarsResources, 5000);
});

function romanToNum(roman) {
    const map = { 'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8 };
    return map[roman] || 0;
}

function getCurrentPlanetName() {
    const activePlanet = document.querySelector('.planet-item.active .planet-name');
    if (activePlanet) return activePlanet.innerText.trim().toUpperCase();
    return 'MARS'; // За замовчуванням
}

function filterModulesByPlanet(modules) {
    const currentPlanet = getCurrentPlanetName();
    const allowedIds = PLANET_MODULE_POOLS[currentPlanet] || [];
    return modules.filter(mod => allowedIds.includes(mod.id));
}

// --- ІНФО ПАНЕЛЬ (З ШЕСТЕРНЕЮ) ---
function resetInfoPanel() {
    selectedModuleKey = null;
    const pTitle = document.getElementById('panelTitle');
    const pDesc = document.getElementById('panelDesc');

    if(pTitle) pTitle.innerText = "ОЧІКУВАННЯ СИСТЕМИ";
    if(pDesc) {
        pDesc.style.textAlign = 'center';
        pDesc.innerHTML = `Натисніть на деталь ракети для сканування<br><br><span class="gear-icon">⚙️</span>`;
    }

    const stats = document.getElementById('statsContainer');
    if (stats) stats.style.display = 'none';

    const btn = document.querySelector('.upgrade-btn');
    if (btn) btn.style.display = 'none';
}

function refreshInfoPanel(key) {
    const stats = document.getElementById('statsContainer');
    if (stats) stats.style.display = 'block';
    
    const pTitle = document.getElementById('panelTitle');
    const pDesc = document.getElementById('panelDesc');
    if(pDesc) pDesc.style.textAlign = 'left';

    const btn = document.querySelector('.upgrade-btn');
    const statLevel = document.getElementById('statLevel');
    const barLevel = document.getElementById('barLevel');
    
    const statIntegrity = document.getElementById('statIntegrity');
    const barIntegrity = document.getElementById('barIntegrity');

    const planetSpecificOwnedModules = filterModulesByPlanet(userOwnedModules);

    let bestModule = null;
    let bestLevel = 0;

    planetSpecificOwnedModules.forEach(mod => {
        if (mod.type === key) {
            let lvl = romanToNum(mod.tier);
            if (lvl > bestLevel) {
                bestLevel = lvl;
                bestModule = mod;
            }
        }
    });

    if (bestModule) {
        pTitle.innerText = bestModule.name.toUpperCase();
        
        let statsText = "СТАТУС: Встановлено\n\nХАРАКТЕРИСТИКИ:\n";
        for (const [statName, statVal] of Object.entries(bestModule.stats)) {
            const statMap = { speed: "Швидкість", armor: "Броня", aerodynamics: "Аеродинаміка", handling: "Керування", damage: "Шкода" };
            const niceName = statMap[statName] || statName;
            statsText += `▸ ${niceName}: +${statVal}\n`;
        }
        pDesc.innerText = statsText;

        if(statLevel) statLevel.innerText = `TIER ${bestModule.tier}`;
        if(barLevel) barLevel.style.width = `${(bestLevel / 8) * 100}%`; 
        
        let efficiency = Math.min(100, 55 + (bestLevel * 6)); 
        if(statIntegrity) statIntegrity.innerText = `${efficiency}%`;
        if(barIntegrity) {
            barIntegrity.style.width = `${efficiency}%`;
            barIntegrity.style.background = '#00ffcc'; 
        }

        if (btn) btn.style.display = 'none'; 
    } else {
        const defaultModules = ['nose', 'body', 'engine', 'fins']; 
        const currentPlanet = getCurrentPlanetName();
        let treeFile = 'tree_Earth.html';
        let planetNiceName = 'ЗЕМЛЯ';

        if(currentPlanet === 'MOON') { treeFile = 'tree_Moon.html'; planetNiceName = 'МІСЯЦЬ'; }
        else if(currentPlanet === 'MARS') { treeFile = 'tree_Mars.html'; planetNiceName = 'МАРС'; }
        else if(currentPlanet === 'JUPITER') { treeFile = 'tree_Jupiter.html'; planetNiceName = 'ЮПІТЕР'; }

        if (defaultModules.includes(key)) {
            pTitle.innerText = "БАЗОВА ДЕТАЛЬ";
            pDesc.innerText = "Це стандартна заводська деталь (Рівень 1).\n\nВона не має додаткових бонусів та характеристик.";
            
            if(statLevel) statLevel.innerText = "TIER I";
            if(barLevel) barLevel.style.width = "12.5%";
            
            if(statIntegrity) statIntegrity.innerText = "50%";
            if(barIntegrity) {
                barIntegrity.style.width = "50%";
                barIntegrity.style.background = '#ffaa00'; 
            }
            
            if (btn) btn.style.display = 'none';
        } else {
            pTitle.innerText = "МОДУЛЬ ВІДСУТНІЙ";
            pDesc.innerText = `Цей слот порожній для планети ${planetNiceName}.\n\nПерейдіть до Дерева розробок, щоб дослідити та встановити необхідні технології.`;
            
            if(statLevel) statLevel.innerText = "TIER 0";
            if(barLevel) barLevel.style.width = "0%";
            
            if(statIntegrity) statIntegrity.innerText = "0%";
            if(barIntegrity) barIntegrity.style.width = "0%";
            
            if (btn) {
                btn.style.display = 'block';
                btn.innerText = `🚀 ДЕРЕВО РОЗРОБОК`;
                btn.style.background = "linear-gradient(90deg, #00ffcc, #00b38f)";
                btn.style.color = "#000";

                btn.onclick = () => {
                    if(typeof window.navigateTo === 'function') window.navigateTo(treeFile);
                    else window.location.href = treeFile + window.location.search;
                };
            }
        }
    }
}

// --- ВЗАЄМОДІЯ ---
function initInteractions() {
    const modules = document.querySelectorAll('.module');
    const panel = document.getElementById('infoPanel');

    modules.forEach(mod => {
        const handleSelect = (e) => {
            e.stopPropagation();
            selectedModuleKey = mod.getAttribute('data-module');
            refreshInfoPanel(selectedModuleKey);
            if(panel) panel.classList.add('active');

            if(e.type === 'click') {
                mod.style.filter = "brightness(2) drop-shadow(0 0 20px white)";
                setTimeout(() => { mod.style.filter = ""; }, 150);
                if(tg.HapticFeedback) tg.HapticFeedback.selectionChanged();
            }
        };

        mod.addEventListener('mouseenter', handleSelect);
        mod.addEventListener('click', handleSelect);
    });

    document.addEventListener('click', (e) => {
        if (panel && !panel.contains(e.target)) {
            resetInfoPanel();
        }
    });
}

// --- НАВІГАЦІЯ ---
// --- НАВІГАЦІЯ ---
function initNavigation() {
    const planets = document.querySelectorAll('.planet-item');
    const searchParams = window.location.search; 

    planets.forEach(planet => {
        planet.addEventListener('click', () => {
            // 1. ПЕРЕВІРКА НА БЛОКУВАННЯ
            if (planet.classList.contains('locked-planet')) {
                alert("❌ Ця планета ще не досліджена! Відкрийте її через головне меню бота.");
                return; // Зупиняємо перехід
            }

            // 2. ОТРИМАННЯ НАЗВИ ТА ПЕРЕХІД
            const nameElement = planet.querySelector('.planet-name');
            if (!nameElement) return;

            const name = nameElement.innerText.trim().toUpperCase();
            let targetPage = '';

            switch (name) {
                case 'EARTH': targetPage = 'index.html'; break;
                case 'MOON':  targetPage = 'Moon.html'; break;
                case 'MARS':  targetPage = 'Mars.html'; break;
                case 'JUPITER': targetPage = 'Jupiter.html'; break;
            }

            if (targetPage) {
                // Використовуємо window.location, щоб гарантовано передати ID
                window.location.href = targetPage + searchParams;
            }
        });
    });

    const treeBtn = document.querySelector('.tech-tree-btn');
    if (treeBtn) {
        treeBtn.addEventListener('click', () => {
            const currentPlanet = getCurrentPlanetName();
            let treeFile = 'tree_Earth.html';
            if(currentPlanet === 'MOON') treeFile = 'tree_Moon.html';
            else if(currentPlanet === 'MARS') treeFile = 'tree_Mars.html';
            else if(currentPlanet === 'JUPITER') treeFile = 'tree_Jupiter.html';

            window.location.href = treeFile + searchParams;
        });
    }

    const inventoryBtn = document.querySelector('.status-badge.inventory-sq');
    if (inventoryBtn) {
        inventoryBtn.addEventListener('click', () => {
            window.location.href = 'inventory.html' + searchParams;
        });
    }
}

// --- ЗІРКИ (Твоя версія) ---
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

// --- ЗАВАНТАЖЕННЯ ДАНИХ ДЛЯ МАРСУ ---
async function updateMarsResources() {
    const urlParams = new URLSearchParams(window.location.search);
    const familyId = urlParams.get('family_id');

    // Якщо ID немає, скрипт зупиняється!
    if (!familyId) {
        console.error("Помилка: відсутній family_id у посиланні!");
        return; 
    }

    try {
        const response = await fetch(`/api/inventory?family_id=${familyId}`);
        if (!response.ok) return;

        const data = await response.json();

        if (data.resources) {
            // Оновлюємо ресурси Марсу
            const coinsEl = document.getElementById('val-coins');
            if (coinsEl) coinsEl.innerText = data.resources.coins;
            
            const siliconEl = document.getElementById('val-silicon');
            if (siliconEl) siliconEl.innerText = data.resources.silicon;
            
            const oxideEl = document.getElementById('val-oxide');
            if (oxideEl) oxideEl.innerText = data.resources.oxide;
        }
        
        // Записуємо модулі для коректної роботи Інфо-панелі
        if (data.modules) {
            userOwnedModules = data.modules;
            if (selectedModuleKey) {
                refreshInfoPanel(selectedModuleKey);
            }
        }

        // --- БЛОКУВАННЯ НЕДОСЛІДЖЕНИХ ПЛАНЕТ ---
        if (data.modules) {
            userOwnedModules = data.modules; 
            
            if (selectedModuleKey) {
                refreshInfoPanel(selectedModuleKey);
            }
        }

        // --- БЛОКУВАННЯ НЕДОСЛІДЖЕНИХ ПЛАНЕТ ---
        if (data.unlocked_planets) {
            const unlockedLower = data.unlocked_planets.map(p => p.toLowerCase());
            const planetItems = document.querySelectorAll('.planet-item');

            planetItems.forEach(item => {
                const planetNameSpan = item.querySelector('.planet-name');
                if (planetNameSpan) {
                    const pName = planetNameSpan.innerText.trim().toLowerCase();
                    // Якщо планети немає в списку відкритих
                    if (!unlockedLower.includes(pName)) {
                        item.classList.add('locked-planet');
                    }
                }
            });
        }

    } catch (error) {
        console.error("Помилка отримання даних з БД:", error);
    }
}