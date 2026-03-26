// JS/config.js

// Зберігаємо ID при завантаженні
const urlParams = new URLSearchParams(window.location.search);
const GLOBAL_FAMILY_ID = urlParams.get('family_id');

if (GLOBAL_FAMILY_ID) {
    console.log("🔒 Session Active. Family ID:", GLOBAL_FAMILY_ID);
} else {
    console.warn("⚠️ No Family ID found. Navigation might be broken.");
}

// 1. АВТОМАТИЧНА ОБРОБКА ВСІХ ПОСИЛАНЬ (<a>)
document.addEventListener('click', function(e) {
    // Шукаємо, чи був клік по посиланню (або всередині нього)
    const link = e.target.closest('a');

    if (link && link.href && GLOBAL_FAMILY_ID) {
        // Ігноруємо js-команди та якорі
        if (link.href.startsWith('javascript') || link.href.includes('#')) return;

        try {
            const url = new URL(link.href, window.location.origin);

            // Якщо ID ще немає в посиланні — додаємо його
            if (!url.searchParams.has('family_id')) {
                url.searchParams.set('family_id', GLOBAL_FAMILY_ID);
                link.href = url.toString(); // Оновлюємо посилання прямо перед переходом
            }
        } catch (err) {
            // Ігноруємо помилки для зовнішніх/дивних посилань
        }
    }
});

// 2. ГЛОБАЛЬНА ФУНКЦІЯ ДЛЯ ПЕРЕХОДУ ЧЕРЕЗ JS
// Використовуйте це замість window.location.href = ...
window.navigateTo = function(page) {
    if (GLOBAL_FAMILY_ID) {
        // Перевіряємо, чи вже є знак питання в посиланні
        const separator = page.includes('?') ? '&' : '?';
        window.location.href = `${page}${separator}family_id=${GLOBAL_FAMILY_ID}`;
    } else {
        window.location.href = page;
    }
};

