const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');

// Змінні для позиції
let currentX = 0; 
let currentY = 0; 
let isDragging = false;
let startX, startY;
let scale = 1;              // Поточний масштаб
const MIN_SCALE = 0.3;      // Мінімальне зменшення
const MAX_SCALE = 3.0;      // Максимальне збільшення
const ZOOM_SPEED = 0.001;
const NODE_WIDTH = 150;
const NODE_HEIGHT = 145;

window.treeNodes = [
    // --- КАТЕГОРІЯ 1: НІС (NOSE) ---
    {
        id: 'gu1',
        name: 'Конус-верхівка',
        tier: 'I',
        desc: 'Аеродинамічний обтікач для зниження опору повітря під час зльоту.',
        x: 1000, y: 1000,
        req: null, owned: true, img: 'images/Nose.png',
        rocketKey: 'nose', level: 1,
        cost: { iron: 0, fuel: 0, coins: 0 } // Вже куплено
    },
    {
        id: 'gu2',
        name: 'Сенсорний шпиль',
        tier: 'II',
        desc: 'Модернізована верхівка з датчиками атмосфери та телеметрією.',
        x: 1400, y: 1000,
        req: 'gu1', owned: false, img: 'images/Nose.png',
        rocketKey: 'nose', level: 2,
        cost: { iron: 500, fuel: 100, coins: 250 } // Коштує ресурсів
    },

    // --- КАТЕГОРІЯ 2: КОРПУС (BODY) ---
    {
        id: 'nc1',
        name: 'Корпус',
        tier: 'I',
        desc: 'Стандартна алюмінієва оболонка для паливних баків.',
        x: 1000, y: 1250,
        req: null, owned: true, img: 'images/Korpus.png',
        rocketKey: 'body', level: 1,
        cost: { iron: 0, fuel: 0, coins: 0 }
    },
    {
        id: 'h1',
        name: 'Сталевий Корпус',
        tier: 'II',
        desc: 'Базова основа ракети. Витримує більші навантаження.',
        x: 1400, y: 1250,
        req: 'nc1', owned: false, img: 'images/Korpus.png',
        rocketKey: 'body', level: 2,
        cost: { iron: 800, fuel: 50, coins: 400 } // Корпус вимагає багато заліза
    },

    // --- КАТЕГОРІЯ 3: ДВИГУН (ENGINE) ---
    {
        id: 'e1',
        name: 'Турбіна',
        tier: 'I',
        desc: 'Базовий насос для подачі паливної суміші в камеру згоряння.',
        x: 1000, y: 1500,
        req: null, owned: true, img: 'images/Turbina.png',
        rocketKey: 'engine', level: 1,
        cost: { iron: 0, fuel: 0, coins: 0 }
    },
    {
        id: 'e2',
        name: 'Турбо-нагнітач',
        tier: 'II',
        desc: 'Подвійна система нагнітання для максимальної тяги двигуна.',
        x: 1400, y: 1500,
        req: 'e1', owned: false, img: 'images/Turbina.png',
        rocketKey: 'engine', level: 2,
        cost: { iron: 400, fuel: 300, coins: 600 } // Двигун дорогий у грошах і паливі
    },

    // --- КАТЕГОРІЯ 4: КРИЛА (FINS) ---
    {
        id: 'a1',
        name: 'Надкрилки',
        tier: 'I',
        desc: 'Пасивні стабілізатори для стійкості ракети в польоті.',
        x: 1000, y: 1750,
        req: null, owned: true, img: 'images/Stabilizator.png',
        rocketKey: 'fins', level: 1,
        cost: { iron: 0, fuel: 0, coins: 0 }
    },
    {
        id: 'a2',
        name: 'Активні закрилки',
        tier: 'II',
        desc: 'Рухомі елементи крил для точного маневрування при посадці.',
        x: 1400, y: 1750,
        req: 'a1', owned: false, img: 'images/Stabilizator.png',
        rocketKey: 'fins', level: 2,
        cost: { iron: 300, fuel: 150, coins: 350 }
    }
];

// --- DRAG LOGIC ---
viewport.addEventListener('mousedown', (e) => {
    if (e.target.closest('.node')) return;
    isDragging = true;
    startX = e.clientX - currentX;
    startY = e.clientY - currentY;
    viewport.style.cursor = 'grabbing';
});

window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    e.preventDefault();
    currentX = e.clientX - startX;
    currentY = e.clientY - startY;
    updateCanvasPosition();
});

window.addEventListener('mouseup', () => {
    isDragging = false;
    viewport.style.cursor = 'grab';
});

function updateCanvasPosition() {
    canvas.style.transform = `translate(${currentX}px, ${currentY}px) scale(${scale})`;
}

// --- INIT ---
async function init() {
    canvas.style.transformOrigin = '0 0';
    
    // --- СИНХРОНІЗАЦІЯ З БАЗОЮ ПЕРЕД МАЛЮВАННЯМ ---
    const urlParams = new URLSearchParams(window.location.search);
    const familyId = urlParams.get('family_id');
    
    if (familyId) {
        try {
            const response = await fetch(`/api/inventory?family_id=${familyId}`);
            const data = await response.json();
            if (data.modules) {
                const ownedIds = data.modules.map(m => m.id);
                window.treeNodes.forEach(node => {
                    if (ownedIds.includes(node.id)) node.owned = true;
                });
            }
        } catch (e) { console.error("DB Sync error:", e); }
    }

    // Малюємо ноди
    treeNodes.forEach(node => {
        const div = document.createElement('div');
        div.className = 'node';
        if (node.owned) div.classList.add('owned', 'researched'); // Додано researched для стилів
        div.id = node.id; // Змінено на чистий ID для легшого пошуку
        
        // Позиціонування
        div.style.left = node.x + 'px';
        div.style.top = node.y + 'px';

        const checkmarkHTML = node.owned ? '<span class="checkmark">✔</span>' : '';
        const imageSrc = node.img ? node.img : 'images/placeholder_icon.png';

        div.innerHTML = `
            <div class="node-img-box">
                <img src="${imageSrc}" class="node-icon" onerror="this.style.opacity=0">
            </div>
            <div class="node-tier">TIER ${node.tier}</div>
            <div class="node-title">${node.name}</div>
            <div class="node-status">${checkmarkHTML}</div>
        `;
        
        div.onclick = (e) => {
            e.stopPropagation();
            highlightPath(node.id);
            openPanel(node);
        };
        canvas.appendChild(div);

        if (node.req) drawLine(node);
    });

    centerViewport();
}

// --- ФУНКЦІЯ ЦЕНТРУВАННЯ ---
function centerViewport() {
    const treeCenterX = 1375; 
    const treeCenterY = 1450;
    const screenCenterX = window.innerWidth / 2;
    const screenCenterY = window.innerHeight / 2;
    currentX = screenCenterX - treeCenterX;
    currentY = screenCenterY - treeCenterY;
    updateCanvasPosition();
}

function drawLine(node) {
    const parent = treeNodes.find(n => n.id === node.req);
    if (!parent) return;

    const line = document.createElement('div');
    line.className = 'line';
    if (node.owned) line.classList.add('highlight'); // Підсвітка лінії, якщо куплено
    line.id = `line-${node.id}`;

    const startX = parent.x + NODE_WIDTH;
    const startY = parent.y + NODE_HEIGHT / 2;
    const endX = node.x;
    const endY = node.y + NODE_HEIGHT / 2;

    const dx = endX - startX;
    const dy = endY - startY;
    const dist = Math.sqrt(dx * dx + dy * dy);

    line.style.width = dist + 'px';
    line.style.left = startX + 'px';
    line.style.top = startY + 'px';
    line.style.transform = `rotate(${Math.atan2(dy, dx)}rad)`;

    canvas.appendChild(line);
}

function highlightPath(nodeId) {
    document.querySelectorAll('.node, .line').forEach(el => el.classList.remove('highlight'));
    let currentId = nodeId;
    while (currentId) {
        document.getElementById(currentId)?.classList.add('highlight'); // Виправлено пошук ID
        document.getElementById(`line-${currentId}`)?.classList.add('highlight');
        const node = treeNodes.find(n => n.id === currentId);
        currentId = node ? node.req : null;
    }
}

function openPanel(node) {
    document.getElementById('node-name').innerText = node.name;
    document.getElementById('node-tier').innerText = `TIER ${node.tier}`;
    document.getElementById('node-desc').innerText = node.desc;
    
    // Передаємо ID в кнопку для функції дослідження
    const actionBtn = document.querySelector('.action-btn');
    actionBtn.onclick = () => investigateModule(node.id);

    const img = document.getElementById('node-image');
    img.src = node.img || 'images/modules/placeholder.png';

    const costContainer = document.getElementById('node-cost');
    
    if (node.owned) {
        costContainer.innerHTML = '<div class="cost-owned-msg">ВЖЕ ВСТАНОВЛЕНО</div>';
        costContainer.classList.add('visible');
        actionBtn.textContent = 'В АНГАРІ';
        actionBtn.classList.add('disabled');
        actionBtn.disabled = true;
    } else {
        const c = node.cost || { iron: 0, fuel: 0, coins: 0 };
        costContainer.innerHTML = `
            <div class="cost-cell">
                <span class="cost-icon">🔩</span>
                <span class="cost-value val-iron">${c.iron}</span>
            </div>
            <div class="cost-cell">
                <span class="cost-icon">⛽</span>
                <span class="cost-value val-fuel">${c.fuel}</span>
            </div>
            <div class="cost-cell">
                <span class="cost-icon">🪙</span>
                <span class="cost-value val-coin">${c.coins}</span>
            </div>
        `;
        costContainer.classList.add('visible');
        actionBtn.textContent = 'ДОСЛІДИТИ';
        actionBtn.classList.remove('disabled');
        actionBtn.disabled = false;
    }

    document.getElementById('info-panel').classList.add('active');
}

function closePanel() {
    document.getElementById('info-panel').classList.remove('active');
    document.querySelectorAll('.node, .line').forEach(el => el.classList.remove('highlight'));
}

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const familyId = urlParams.get('family_id');
    
    // Виправлено пошук кнопки (клас .back-btn як у вашому HTML)
    const backBtn = document.querySelector('.back-btn'); 
    const path = window.location.pathname;
    
    if (backBtn) {
        const routes = {
            'tree_Earth.html': { url: 'index.html', text: 'ГОЛОВНА' },
            'tree_Moon.html':  { url: 'Moon.html',  text: 'МІСЯЦЬ' },
            'tree_Mars.html':  { url: 'Mars.html',  text: 'МАРС' },
            'tree_Jupiter.html': { url: 'Jupiter.html', text: 'ЮПІТЕР' }
        };

        for (const [key, route] of Object.entries(routes)) {
            if (path.includes(key)) {
                backBtn.href = familyId ? `${route.url}?family_id=${familyId}` : route.url;
                backBtn.innerHTML = `<span class="arrow">‹</span> ${route.text}`;
                break; 
            }
        }
    }
});

// --- ЛОГІКА ЗУМУ ---
viewport.addEventListener('wheel', (e) => {
    e.preventDefault();
    const xs = (e.clientX - currentX) / scale;
    const ys = (e.clientY - currentY) / scale;
    const delta = -e.deltaY;
    const factor = (delta > 0) ? 1.1 : 0.9;
    let newScale = scale * factor;
    if (newScale < MIN_SCALE) newScale = MIN_SCALE;
    if (newScale > MAX_SCALE) newScale = MAX_SCALE;
    currentX -= xs * (newScale - scale);
    currentY -= ys * (newScale - scale);
    scale = newScale;
    updateCanvasPosition();
}, { passive: false });

async function investigateModule(moduleId) {
    const urlParams = new URLSearchParams(window.location.search);
    const familyId = urlParams.get('family_id');

    if (!familyId) {
        alert("Помилка: ID сім'ї не знайдено!");
        return;
    }

    try {
        const response = await fetch('/api/investigate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ family_id: familyId, module_id: moduleId })
        });

        const result = await response.json();

        if (response.ok) {
            const moduleElement = document.getElementById(moduleId);
            if (moduleElement) {
                moduleElement.classList.add('owned', 'researched');
                const checkStatus = moduleElement.querySelector('.node-status');
                if (checkStatus) checkStatus.innerHTML = '<span class="checkmark">✔</span>';
            }
            alert("Модуль успішно досліджено!");
            location.reload(); // Перезавантаження для оновлення масиву та ліній
        } else {
            alert("Помилка: " + result.error);
        }
    } catch (error) {
        console.error("Помилка запиту:", error);
    }
}

// Запуск ініціалізації
window.onload = init;