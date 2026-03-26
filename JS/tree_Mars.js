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
    // === ГРУПА 1: КОРПУС ТА ЕНЕРГІЯ ===
    { 
        id: 'g1_1', name: 'Вантажний Відсік', tier: 'III', 
        desc: 'Базовий модуль для перевезення марсіанських мінералів.', 
        x: 1000, y: 1000, req: null, owned: true, img: 'images/Korpus.png',
        cost: { silicon: 0, oxide: 0, coins: 0 }
    },
    { 
        id: 'g1_2', name: 'Герметизація', tier: 'IV', 
        desc: 'Посилена ізоляція для захисту від піщаних бурь та низького тиску.', 
        x: 1250, y: 1000, req: 'g1_1', owned: false, img: 'images/Korpus.png',
        cost: { silicon: 900, oxide: 500, coins: 2500 }
    },
    { 
        id: 'g1_up', name: 'Панель Оновлення', tier: 'III', 
        desc: 'Система управління живленням для колоніальних модулів.', 
        x: 1500, y: 900, req: 'g1_2', owned: false, img: 'images/Korpus.png',
        cost: { silicon: 1200, oxide: 800, coins: 3500 }
    },
    { 
        id: 'g1_down', name: 'Сонячні Панелі', tier: 'V', 
        desc: 'Фотоелементи, адаптовані до спектру сонячного світла на Марсі.', 
        x: 1500, y: 1100, req: 'g1_2', owned: false, img: 'images/Bataries.png',
        cost: { silicon: 1000, oxide: 600, coins: 3000 }
    },
    { 
        id: 'g1_end', name: 'Нові Панелі MK-II', tier: 'VI', 
        desc: 'Високоефективні панелі з системою самоочищення від пилу.', 
        x: 1750, y: 1100, req: 'g1_down', owned: false, img: 'images/Bataries.png',
        cost: { silicon: 1500, oxide: 1000, coins: 5000 }
    },

    // === ГРУПА 2: ДВИГУНИ ===
    { 
        id: 'g2_1', name: 'Турбо-Форсаж', tier: 'III', 
        desc: 'Система впорскування для прискорення в розрідженій атмосфері.', 
        x: 1000, y: 1400, req: null, owned: true, img: 'images/Turbina.png',
        cost: { silicon: 0, oxide: 0, coins: 0 }
    },
    { 
        id: 'g2_up', name: 'Покращений Форсаж', tier: 'IV', 
        desc: 'Оптимізована камера згоряння на кремнієвих присадках.', 
        x: 1250, y: 1300, req: 'g2_1', owned: false, img: 'images/Turbina.png',
        cost: { silicon: 1800, oxide: 1200, coins: 4500 }
    },
    { 
        id: 'g2_down', name: 'Бокові Турбіни', tier: 'III', 
        desc: 'Додаткові маневрові двигуни для стабілізації в бурях.', 
        x: 1250, y: 1500, req: 'g2_1', owned: false, img: 'images/Turbina.png',
        cost: { silicon: 1200, oxide: 800, coins: 3200 }
    },

    // === ГРУПА 3: ЗАХИСТ ТА ЗБРОЯ ===
    { 
        id: 'g3_a1', name: 'Керамічний Щит', tier: 'III', 
        desc: 'Термостійке покриття, стійке до абразивного впливу пилу.', 
        x: 1000, y: 1700, req: null, owned: true, img: 'images/Nose.png',
        cost: { silicon: 0, oxide: 0, coins: 0 }
    },
    { 
        id: 'g3_a2', name: 'Титановий Конус', tier: 'IV', 
        desc: 'Посилений конус для захисту при вході в атмосферу.', 
        x: 1250, y: 1700, req: 'g3_a1', owned: false, img: 'images/Nose.png',
        cost: { silicon: 1100, oxide: 600, coins: 2800 }
    },
    { 
        id: 'g3_b1', name: 'Бластер', tier: 'I', 
        desc: 'Стандартний лазер для розчищення шляху від метеоритів.', 
        x: 1000, y: 1900, req: null, owned: true, img: 'images/Blasters.png',
        cost: { silicon: 0, oxide: 0, coins: 0 }
    },
    { 
        id: 'g3_b2', name: 'Покращений Бластер', tier: 'II', 
        desc: 'Потужна гармата для захисту марсіанських конвоїв.', 
        x: 1250, y: 1900, req: 'g3_b1', owned: false, img: 'images/Blasters.png',
        cost: { silicon: 2000, oxide: 1500, coins: 5000 }
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
        const c = node.cost || {};
        
        // Визначаємо ресурси саме для Марса
        // Якщо silicon або oxide відсутні в об'єкті, використовуємо 0
        const siliconVal = c.silicon !== undefined ? c.silicon : (c.iron || 0);
        const oxideVal = c.oxide !== undefined ? c.oxide : (c.fuel || 0);
        const coinsVal = c.coins || 0;

        costContainer.innerHTML = `
            <div class="cost-cell">
                <span class="cost-icon">🧱</span>
                <span class="cost-value">${siliconVal}</span>
            </div>
            <div class="cost-cell">
                <span class="cost-icon">🧪</span>
                <span class="cost-value">${oxideVal}</span>
            </div>
            <div class="cost-cell">
                <span class="cost-icon">🪙</span>
                <span class="cost-value">${coinsVal}</span>
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