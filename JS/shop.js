const tg = window.Telegram.WebApp;
tg.expand();

// Отримуємо family_id з URL (як ви робили на головній сторінці)
const urlParams = new URLSearchParams(window.location.search);
const familyId = urlParams.get('family_id');

let userBalance = 0;
let currentOffers = [];

// 1. Оновлення балансу (беремо з існуючого API інвентарю)
async function fetchBalance() {
    try {
        const response = await fetch(`/api/inventory?family_id=${familyId}`);
        const data = await response.json();
        if (data.resources) {
            userBalance = data.resources.coins;
            document.getElementById('user-balance').innerText = userBalance;
            updateButtonsState(); // Оновлюємо доступність кнопок
        }
    } catch (err) {
        console.error("Помилка балансу:", err);
    }
}

// 2. Отримання щоденних акцій
async function fetchOffers() {
    try {
        // ДОДАЛИ ?family_id=${familyId}
        const response = await fetch(`/api/daily_offers?family_id=${familyId}`);
        const data = await response.json();
        currentOffers = data.offers;
        renderOffers();
    } catch (err) {
        document.getElementById('offers-container').innerHTML = `<p style="color:red; text-align:center;">Помилка зв'язку з сервером</p>`;
    }
}

// 3. Відмальовка карток товарів
// 3. Відмальовка карток товарів
function renderOffers() {
    const container = document.getElementById('offers-container');
    container.innerHTML = '';

    currentOffers.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'offer-card';
        
        // Формуємо HTML для ціни та тегу залежно від розміру знижки
        let tagHtml = '';
        let priceHtml = '';

        if (item.discount === 100) {
            tagHtml = `<div class="discount-tag free">FREE</div>`;
            priceHtml = `<span class="new-price free-text">БЕЗКОШТОВНО</span>`;
        } else if (item.discount > 0) {
            tagHtml = `<div class="discount-tag">-${item.discount}%</div>`;
            priceHtml = `
                <span class="old-price">${item.old_price}</span>
                <span class="new-price">🪙 ${item.price}</span>
            `;
        } else {
            // Товар без знижки
            priceHtml = `<span class="new-price" style="color: #fff;">🪙 ${item.price}</span>`;
        }
        
        card.innerHTML = `
            ${tagHtml}
            <div class="offer-header">
                <div class="offer-icon">${item.icon}</div>
                <div>
                    <h3 class="offer-title">${item.name}</h3>
                    <div class="offer-amount">+${item.amount} шт.</div>
                </div>
            </div>
            <div class="price-container">
                ${priceHtml}
            </div>
            <button class="buy-btn" id="btn-${index}" onclick="buyItem(${index})">ПРИДБАТИ</button>
        `;
        container.appendChild(card);
    });
    updateButtonsState();
}

// 4. Перевірка, чи вистачає грошей на покупку
function updateButtonsState() {
    currentOffers.forEach((item, index) => {
        const btn = document.getElementById(`btn-${index}`);
        if (btn) {
            // ПЕРЕВІРКА: чи куплений товар
            if (item.purchased) {
                btn.disabled = true;
                btn.innerText = "ПРИДБАНО ✓";
                btn.style.background = "#222"; // Темно-сірий колір
                btn.style.color = "#666";
                btn.style.boxShadow = "none";
                btn.style.border = "1px solid #333";
            } 
            // Якщо ще не куплений, але немає грошей
            else if (userBalance < item.price) {
                btn.disabled = true;
                btn.innerText = "НЕМАЄ КОШТІВ";
                btn.style.background = "#444";
                btn.style.color = "#888";
                btn.style.boxShadow = "none";
            } 
            // Доступно для покупки
            else {
                btn.disabled = false;
                btn.innerText = "ПРИДБАТИ";
                btn.style.background = "linear-gradient(90deg, #00b38f, #00ffcc)";
                btn.style.color = "#000";
                btn.style.boxShadow = "0 0 15px rgba(0, 255, 204, 0.3)";
            }
        }
    });
}

// 5. Логіка покупки
async function buyItem(index) {
    const item = currentOffers[index];
    const btn = document.getElementById(`btn-${index}`);
    
    btn.disabled = true;
    btn.innerText = "ОБРОБКА...";
    tg.HapticFeedback.impactOccurred('medium');

    try {
        const response = await fetch('/api/buy_shop_item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                family_id: familyId,
                item: item
            })
        });

        const result = await response.json();

        if (response.ok) {
            item.purchased = true; // Локально позначаємо як куплене
            showToast(`Успішно придбано: ${item.name}!`);
            tg.HapticFeedback.notificationOccurred('success');
            fetchBalance(); // Оновить баланс і заблокує кнопку (викличе updateButtonsState)
        } else {
            showToast(result.error || "Помилка покупки", true);
            tg.HapticFeedback.notificationOccurred('error');
            updateButtonsState(); // Повертає кнопку у нормальний стан
        }
    } catch (err) {
        showToast("Помилка з'єднання", true);
        updateButtonsState();
    }
}

// 6. Таймер до опівночі (оновлення асортименту)
function startCountdown() {
    function updateTimer() {
        const now = new Date();
        // Розраховуємо час до наступної опівночі
        const tomorrow = new Date(now);
        tomorrow.setHours(24, 0, 0, 0);
        
        const diff = tomorrow - now;
        
        const h = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const s = Math.floor((diff % (1000 * 60)) / 1000);
        
        document.getElementById('countdown').innerText = 
            `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    
    updateTimer();
    setInterval(updateTimer, 1000);
}

// 7. Повідомлення (Toast)
function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    toast.innerText = message;
    toast.style.background = isError ? 'rgba(255, 0, 85, 0.9)' : 'rgba(0, 255, 204, 0.9)';
    toast.style.boxShadow = isError ? '0 0 20px rgba(255, 0, 85, 0.5)' : '0 0 20px rgba(0, 255, 204, 0.5)';
    toast.style.color = isError ? '#fff' : '#000';
    
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Ініціалізація при завантаженні сторінки
if (familyId) {
    // Створюємо асинхронну функцію, щоб запити йшли СУВОРО по черзі
    async function initShop() {
        await fetchBalance(); // 1. Спочатку чекаємо завантаження монет
        await fetchOffers();  // 2. Тільки після цього вантажимо товари
        startCountdown();     // 3. Запускаємо таймер
    }
    
    initShop(); // Запускаємо нашу чергу
} else {
    document.getElementById('offers-container').innerHTML = `<p style="color:red; text-align:center;">Помилка: Не вказано ID сім'ї</p>`;
}