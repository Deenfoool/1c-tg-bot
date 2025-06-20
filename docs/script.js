const ITEMS_PER_PAGE = 5;

let nomenclature = [];
let currentPage = 0;

// Получение данных от сервера (ваш бэкенд)
async function fetchNomenclature() {
    try {
        const response = await fetch('https://your-api-url.com/nomenclature'); 
        if (!response.ok) throw new Error("Ошибка при получении данных");
        nomenclature = await response.json();
        renderItems();
    } catch (e) {
        document.getElementById('items').innerHTML = `<p>❌ Ошибка: ${e.message}</p>`;
    }
}

function renderItems() {
    const itemsDiv = document.getElementById('items');
    itemsDiv.innerHTML = '';
    const start = currentPage * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    const pageItems = nomenclature.slice(start, end);

    for (let item of pageItems) {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `
            <b>Код:</b> <code>${item.code}</code><br>
            <b>Наименование:</b> ${escapeHtml(item.name)}
        `;
        itemsDiv.appendChild(div);
    }

    updatePaginationInfo();
}

function escapeHtml(text) {
    return text.replace(/&/g, '&amp;')
               .replace(/</g, '<')
               .replace(/>/g, '>');
}

function nextPage() {
    if ((currentPage + 1) * ITEMS_PER_PAGE < nomenclature.length) {
        currentPage++;
        renderItems();
    }
}

function prevPage() {
    if (currentPage > 0) {
        currentPage--;
        renderItems();
    }
}

function handleSearch() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const filtered = nomenclature.filter(item =>
        item.code.includes(query) || item.name.toLowerCase().includes(query)
    );
    nomenclature = filtered;
    currentPage = 0;
    renderItems();
}

function updatePaginationInfo() {
    const totalPages = Math.ceil(nomenclature.length / ITEMS_PER_PAGE);
    document.getElementById('pageInfo').textContent = `Страница ${currentPage + 1} из ${totalPages}`;
}

// Запуск приложения
Telegram.WebApp.ready();
Telegram.WebApp.expand();

fetchNomenclature();
