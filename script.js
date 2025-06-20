const ITEMS_PER_PAGE = 5;

let nomenclature = [];
let currentPage = 0;

// Получение данных от сервера
async function fetchNomenclature() {
    try {
        const response = await fetch('https://1c-tg-bot-deenfoool.amvera.io/api/nomenclature'); 
        if (!response.ok) throw new Error("Ошибка загрузки данных");
        nomenclature = await response.json();
        renderItems();
    } catch (e) {
        document.getElementById('items').innerHTML = `<p>❌ Ошибка: ${e.message}</p>`;
    }
}

function escapeHtml(text) {
    return text.replace(/&/g, '&amp;')
               .replace(/</g, '<')
               .replace(/>/g, '>');
}

async function fetchNomenclature() {
    try {
        const response = await fetch('https://1c-tg-bot-deenfoool.amvera.io/api/nomenclature'); 
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
            <div>
                <b>Код:</b> <code>${item.code}</code><br>
                <b>Наименование:</b> ${escapeHtml(item.name)}
            </div>
            <button class="delete-btn" onclick="deleteItem('${item.code}')">🗑️</button>
        `;
        itemsDiv.appendChild(div);
    }

    updatePaginationInfo();
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

// Добавление новой записи
async function addItem() {
    const code = document.getElementById('newCode').value.trim();
    const name = document.getElementById('newName').value.trim();

    if (!code || !name) {
        alert("❌ Заполните все поля.");
        return;
    }

    if (code.length < 5 || !/^\d+$/.test(code)) {
        alert("❌ Код должен быть не менее 5 цифр.");
        return;
    }

    const existing = nomenclature.find(item => item.code === code);
    if (existing) {
        alert("❌ Запись с этим кодом уже существует.");
        return;
    }

    // Отправляем POST-запрос к API
    const res = await fetch('https://1c-tg-bot-deenfoool.amvera.io/api/add',  {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, name })
    });

    if (res.ok) {
        nomenclature.push({ code, name });
        hideAddForm();
        renderItems();
        alert("✅ Запись добавлена.");
    } else {
        alert("❌ Не удалось добавить запись.");
    }
}

// Удаление записи
async function deleteItem(code) {
    const res = await fetch(`https://1c-tg-bot-deenfoool.amvera.io/api/delete/${code}`,  {
        method: 'DELETE'
    });

    if (res.ok) {
        nomenclature = nomenclature.filter(item => item.code !== code);
        renderItems();
        alert("✅ Запись удалена.");
    } else {
        alert("❌ Не удалось удалить запись.");
    }
}

// Импорт из .txt
async function importData() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.txt';

    fileInput.onchange = async () => {
        const file = fileInput.files[0];
        const reader = new FileReader();

        reader.onload = async () => {
            const lines = reader.result.split('\n').filter(line => line.trim());

            const data = lines.map(line => {
                const [code, name] = line.split(' ', 2);
                return { code, name };
            });

            const res = await fetch('https://1c-tg-bot-deenfoool.amvera.io/api/import',  {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                alert("✅ Данные успешно импортированы.");
                fetchNomenclature();
            } else {
                alert("❌ Ошибка импорта.");
            }
        };

        reader.readAsText(file);
    };

    fileInput.click();
}

// Показать форму добавления
function toggleAddForm() {
    const form = document.getElementById('addForm');
    form.style.display = form.style.display === 'none' ? 'flex' : 'none';
}

function hideAddForm() {
    document.getElementById('addForm').style.display = 'none';
    document.getElementById('newCode').value = '';
    document.getElementById('newName').value = '';
}

// Запуск приложения
Telegram.WebApp.ready();
Telegram.WebApp.expand();

fetchNomenclature();
