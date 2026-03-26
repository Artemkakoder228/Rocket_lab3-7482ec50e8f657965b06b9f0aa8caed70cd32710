document.addEventListener('DOMContentLoaded', () => {
    console.log("Inventory script loaded"); // Лог для перевірки, що скрипт стартував

    const backBtn = document.getElementById('back-btn');

    // 1. Отримуємо family_id з URL (наприклад, inventory.html?family_id=123)
    const urlParams = new URLSearchParams(window.location.search);
    const familyId = urlParams.get('family_id');

    console.log("Family ID found:", familyId); // Лог ID

    if (familyId) {
        // Зберігаємо ID для кнопки "Назад", щоб не загубити його при виході
        if (backBtn) backBtn.href = `index.html?family_id=${familyId}`;

        // Запускаємо завантаження інвентарю
        loadInventory(familyId);
    } else {
        console.warn("No family_id provided!");
        showError("Помилка: Не знайдено ID гравця. Зайдіть в гру через головне меню.");
    }
});

/**
 * Функція для показу помилок прямо на екрані (замість console)
 */
function showError(msg) {
    const grid = document.getElementById('resources-grid');
    if (grid) {
        grid.innerHTML = `<div style="color: #ff4d4d; padding: 20px; text-align: center; border: 1px solid red; background: rgba(0,0,0,0.7);">
            ⚠️ ${msg}
        </div>`;
    }
}

/**
 * Завантажує дані з сервера
 */
async function loadInventory(familyId) {
    try {
        console.log(`Fetching: /api/inventory?family_id=${familyId}`);

        const response = await fetch(`/api/inventory?family_id=${familyId}`);

        if (!response.ok) {
            throw new Error(`Помилка сервера: ${response.status}`);
        }

        const data = await response.json();
        console.log("Data received:", data); // Показує в консолі, що прийшло

        if (data.error) {
            showError("Сервер повернув помилку: " + data.error);
            return;
        }

        // Перевіряємо, чи прийшли ресурси
        if (!data.resources) {
            showError("Дані про ресурси відсутні у відповіді сервера.");
            return;
        }

        renderResources(data.resources);
        renderModules(data.modules);

    } catch (e) {
        console.error("Connection error:", e);
        showError("Не вдалося з'єднатися з сервером. Перевірте, чи запущено Python-бот.");
    }
}

/**
 * Малює ресурси
 */
function renderResources(res) {
    const container = document.getElementById('resources-grid');
    if (!container) return;

    container.innerHTML = '';

    // Список ресурсів і їх налаштування
    const resourceMap = [
        { key: 'coins', name: 'Спейскоіни', icon: '🪙', color: '#00ff9d' },
        { key: 'iron', name: 'Залізо', icon: '🔩', color: '#aebbc9' },
        { key: 'fuel', name: 'Паливо', icon: '💠', color: '#ff9d00' },
        { key: 'regolith', name: 'Реголіт', icon: '🌑', color: '#8e8e8e' },
        { key: 'he3', name: 'Гелій-3', icon: '💎', color: '#00f2ff' },
        { key: 'silicon', name: 'Кремній', icon: '💾', color: '#32a852' },
        { key: 'oxide', name: 'Оксид', icon: '🧪', color: '#a83232' },
        { key: 'hydrogen', name: 'Водень', icon: '🎈', color: '#3262a8' },
        { key: 'helium', name: 'Гелій', icon: '🌌', color: '#6a32a8' }
    ];

    let count = 0;
    resourceMap.forEach(item => {
        // Відображаємо, навіть якщо ресурсу 0 (але не якщо undefined)
        if (res[item.key] !== undefined && res[item.key] !== null) {
            const card = document.createElement('div');
            card.className = 'res-card';

            // Стилі прямо тут, щоб гарантувати відображення
            card.style.borderColor = item.color;
            card.style.display = 'flex';
            card.style.alignItems = 'center';
            card.style.background = 'rgba(0, 0, 0, 0.6)';
            card.style.padding = '10px';
            card.style.borderRadius = '8px';
            card.style.marginBottom = '10px';
            card.style.border = `1px solid ${item.color}`;
            card.style.boxShadow = `0 0 10px ${item.color}40`;

            card.innerHTML = `
                <div class="res-icon" style="font-size: 2em; margin-right: 15px;">${item.icon}</div>
                <div class="res-info" style="display: flex; flex-direction: column;">
                    <span class="res-name" style="font-size: 0.8em; opacity: 0.8; color: #ccc;">${item.name}</span>
                    <span class="res-amount" style="color:${item.color}; font-weight: bold; font-size: 1.2em;">
                        ${res[item.key]}
                    </span>
                </div>
            `;
            container.appendChild(card);
            count++;
        }
    });

    if (count === 0) {
        container.innerHTML = '<div style="padding:20px; color: white;">Ресурсів не знайдено (0).</div>';
    }
}

/**
 * Малює модулі
 */
function renderModules(modules) {
    const container = document.getElementById('modules-grid');
    if (!container) return;

    container.innerHTML = '';

    if (!modules || modules.length === 0) {
        container.innerHTML = '<div style="color:gray; padding:20px; text-align:center; width:100%;">Ангар порожній.</div>';
        return;
    }

    modules.forEach(mod => {
        const card = document.createElement('div');
        card.className = 'mod-card';

        // Вибираємо картинку
        let imgPath = 'images/modules/placeholder.png';
        if (mod.type === 'nose') imgPath = 'images/Nose.png';
        if (mod.type === 'body') imgPath = 'images/Korpus.png';
        if (mod.type === 'engine') imgPath = 'images/Turbina.png';
        if (mod.type === 'fins') imgPath = 'images/Stabilizator.png';

        card.innerHTML = `
            <div class="mod-img-box">
                <img src="${imgPath}" alt="${mod.name}" style="max-width: 50px; height: auto;" onerror="this.src='images/Logo_for_site.png'">
            </div>
            <div class="mod-body">
                <h3 class="mod-name" style="margin: 0; font-size: 1em; color: white;">${mod.name}</h3>
                <span class="mod-tier" style="font-size: 0.8em; color: #ffd700;">TIER ${mod.tier || 'I'}</span>
            </div>
        `;
        container.appendChild(card);
    });
}