const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');

// Змінні для позиції та зуму
let currentX = 0; 
let currentY = 0; 
let isDragging = false;
let startX, startY;
let scale = 1;              
const MIN_SCALE = 0.3;      
const MAX_SCALE = 3.0;      

// Для телефонів (Pinch-to-zoom)
let initialPinchDistance = null;
let initialScale = 1;

const NODE_WIDTH = 150;
const NODE_HEIGHT = 145;

window.treeNodes = [
    { 
        id: 'root1', name: 'Сталевий Корпус', tier: 'II', desc: 'Базова основа ракети, адаптована для місячних умов.', 
        x: 1000, y: 1100, req: null, owned: false, img: 'images/Korpus.png',
        cost: { regolith: 0, he3: 0, coins: 0 }
    },
    { 
        id: 'branch1_up1', name: 'Вантажний Відсік', tier: 'III', desc: 'Додатковий модуль для транспортування видобутого реголіту.', 
        x: 1300, y: 1000, req: 'root1', owned: false, img: 'images/Korpus.png',
        cost: { regolith: 500, he3: 200, coins: 800 }
    },
    { 
        id: 'branch1_up2', name: 'Сонячні Панелі', tier: 'IV', desc: 'Ефективна генерація енергії в умовах відсутності атмосфери.', 
        x: 1600, y: 1000, req: 'branch1_up1', owned: false, img: 'images/Bataries.png',
        cost: { regolith: 700, he3: 400, coins: 1200 }
    },
    { 
        id: 'branch1_down1', name: 'Аеро-надкрилки', tier: 'III', desc: 'Стабілізація для маневрування на низькій навколомісячній орбіті.', 
        x: 1300, y: 1200, req: 'root1', owned: false, img: 'images/Stabilizator.png',
        cost: { regolith: 400, he3: 150, coins: 900 }
    },
    { 
        id: 'root2', name: 'Турбо-нагнітач', tier: 'II', desc: 'Подвійна система нагнітання для роботи на суміші гелію.', 
        x: 1000, y: 1550, req: null, owned: false, img: 'images/Turbina.png',
        cost: { regolith: 0, he3: 0, coins: 0 }
    },
    { 
        id: 'branch2_up', name: 'Турбо-Форсаж', tier: 'III', desc: 'Покращена турбіна для швидкого зльоту з поверхні Місяця.', 
        x: 1300, y: 1450, req: 'root2', owned: false, img: 'images/Turbina.png',
        cost: { regolith: 800, he3: 600, coins: 1500 }
    },
    { 
        id: 'branch2_down', name: 'Бокові Рушії', tier: 'II', desc: 'Маневрені турбіни для точної посадки в кратери.', 
        x: 1300, y: 1650, req: 'root2', owned: false, img: 'images/Turbina.png',
        cost: { regolith: 600, he3: 400, coins: 1000 }
    },
    { 
        id: 'root3', name: 'Сенсорний шпиль', tier: 'II', desc: 'Модернізована верхівка з датчиками космічного випромінювання.', 
        x: 1000, y: 1900, req: null, owned: false, img: 'images/Nose.png',
        cost: { regolith: 0, he3: 0, coins: 0 }
    },
    { 
        id: 'branch3', name: 'Керамічний Щит', tier: 'III', desc: 'Захист верхівки від мікрометеоритів та місячного пилу.', 
        x: 1300, y: 1900, req: 'root3', owned: false, img: 'images/Nose.png',
        cost: { regolith: 500, he3: 300, coins: 1100 }
    }
];

// ===================================================================
// --- РУХ ТА ЗУМ ДЛЯ ПК І ТЕЛЕФОНІВ (МИШКА + СЕНСОРНІ ЕКРАНИ) ---
// ===================================================================

function updateCanvasPosition() {
    canvas.style.transform = `translate(${currentX}px, ${currentY}px) scale(${scale})`;
}

// --- 1. КЕРУВАННЯ МИШКОЮ (ПК) ---
viewport.addEventListener('mousedown', (e) => {
    if (e.target.closest('.node') || e.target.closest('.action-btn') || e.target.closest('.back-btn')) return;
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

viewport.addEventListener('wheel', (e) => {
    e.preventDefault();
    const xs = (e.clientX - currentX) / scale;
    const ys = (e.clientY - currentY) / scale;
    const factor = (e.deltaY > 0) ? 0.9 : 1.1; 
    let newScale = scale * factor;
    newScale = Math.max(MIN_SCALE, Math.min(newScale, MAX_SCALE));
    currentX -= xs * (newScale - scale);
    currentY -= ys * (newScale - scale);
    scale = newScale;
    updateCanvasPosition();
}, { passive: false });

// --- 2. КЕРУВАННЯ ПАЛЬЦЯМИ (ТЕЛЕФОН) ---
viewport.addEventListener('touchstart', (e) => {
    if (e.target.closest('.node') || e.target.closest('.action-btn') || e.target.closest('.back-btn')) return;
    
    if (e.touches.length === 1) {
        isDragging = true;
        startX = e.touches[0].clientX - currentX;
        startY = e.touches[0].clientY - currentY;
    } else if (e.touches.length === 2) {
        isDragging = false; 
        initialPinchDistance = Math.hypot(
            e.touches[0].clientX - e.touches[1].clientX,
            e.touches[0].clientY - e.touches[1].clientY
        );
        initialScale = scale;
    }
}, { passive: false });

window.addEventListener('touchmove', (e) => {
    if (!isDragging && !initialPinchDistance) return;
    
    if (e.cancelable) e.preventDefault();

    if (e.touches.length === 1 && isDragging) {
        currentX = e.touches[0].clientX - startX;
        currentY = e.touches[0].clientY - startY;
        updateCanvasPosition();
    } else if (e.touches.length === 2 && initialPinchDistance) {
        const currentPinchDistance = Math.hypot(
            e.touches[0].clientX - e.touches[1].clientX,
            e.touches[0].clientY - e.touches[1].clientY
        );
        
        const centerX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
        const centerY = (e.touches[0].clientY + e.touches[1].clientY) / 2;

        const xs = (centerX - currentX) / scale;
        const ys = (centerY - currentY) / scale;

        let newScale = initialScale * (currentPinchDistance / initialPinchDistance);
        newScale = Math.max(MIN_SCALE, Math.min(newScale, MAX_SCALE));

        currentX -= xs * (newScale - scale);
        currentY -= ys * (newScale - scale);
        scale = newScale;
        updateCanvasPosition();
    }
}, { passive: false });

window.addEventListener('touchend', (e) => {
    if (e.touches.length < 2) initialPinchDistance = null;
    if (e.touches.length === 0) isDragging = false;
});

// ===================================================================
// --- ІНІЦІАЛІЗАЦІЯ ДЕРЕВА ТА БД ---
// ===================================================================

async function init() {
    canvas.style.transformOrigin = '0 0';
    
    // --- СИНХРОНІЗАЦІЯ З БАЗОЮ ПЕРЕД МАЛЮВАННЯМ ---
    const urlParams = new URLSearchParams(window.location.search);
    const familyId = urlParams.get('family_id');
    
    if (familyId) {
        try {
            const response = await fetch(`/api/inventory?family_id=${familyId}`);
            const data = await response.json();
            
            // 1. Відмічаємо куплені модулі
            if (data.modules) {
                const ownedIds = data.modules.map(m => m.id);
                window.treeNodes.forEach(node => {
                    if (ownedIds.includes(node.id)) node.owned = true;
                });
            }

            // 2. БЛОКУВАННЯ НЕДОСЛІДЖЕНИХ ПЛАНЕТ
            if (data.unlocked_planets) {
                const navButtons = document.querySelectorAll('.planet-btn');
                const unlockedLower = data.unlocked_planets.map(p => p.toLowerCase());

                navButtons.forEach(btn => {
                    // Отримуємо назву планети з тексту кнопки (EARTH, MOON...)
                    const planetNameBtn = btn.textContent.trim().toLowerCase();
                    
                    if (!unlockedLower.includes(planetNameBtn)) {
                        // Якщо планета не відкрита
                        btn.classList.add('locked-planet');
                        btn.href = 'javascript:void(0);'; // Скасовуємо перехід
                        btn.onclick = (e) => {
                            e.preventDefault();
                            alert("❌ Ця планета ще не досліджена! Відкрийте її через головне меню бота.");
                        };
                    } else {
                        // Якщо відкрита — додаємо family_id до посилання, щоб не вибивало з акаунту при перемиканні
                        const originalHref = btn.getAttribute('href');
                        if (originalHref && !originalHref.includes('family_id') && !originalHref.includes('javascript')) {
                            btn.href = `${originalHref}?family_id=${familyId}`;
                        }
                    }
                });
            }

        } catch (e) { console.error("DB Sync error:", e); }
    }

    treeNodes.forEach(node => {
        const div = document.createElement('div');
        div.className = 'node';
        if (node.owned) div.classList.add('owned', 'researched'); 
        div.id = node.id; 
        
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
    if (node.owned) line.classList.add('highlight'); 
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
        document.getElementById(currentId)?.classList.add('highlight'); 
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
        
        const isMoon = c.regolith !== undefined;
        
        const res1Icon = isMoon ? '🌑' : '⚙️'; 
        const res1Value = isMoon ? c.regolith : c.iron;
        
        const res2Icon = isMoon ? '🧪' : '⚛️'; 
        const res2Value = isMoon ? c.he3 : c.fuel;

        costContainer.innerHTML = `
            <div class="cost-cell">
                <span class="cost-icon">${res1Icon}</span>
                <span class="cost-value">${res1Value || 0}</span>
            </div>
            <div class="cost-cell">
                <span class="cost-icon">${res2Icon}</span>
                <span class="cost-value">${res2Value || 0}</span>
            </div>
            <div class="cost-cell">
                <span class="cost-icon">🪙</span>
                <span class="cost-value">${c.coins || 0}</span>
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
            location.reload(); 
        } else {
            alert("Помилка: " + result.error);
        }
    } catch (error) {
        console.error("Помилка запиту:", error);
    }
}

// Запуск ініціалізації
window.onload = init;