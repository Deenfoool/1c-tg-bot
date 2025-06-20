import React, { useState, useEffect } from 'react';

const App = () => {
  const [nomenclature, setNomenclature] = useState([]);
  const [activeTab, setActiveTab] = useState('list');
  const [newItem, setNewItem] = useState({ code: '', name: '' });
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(0);
  const ITEMS_PER_PAGE = 5;

  // Загрузка данных из Telegram-бота
  const fetchNomenclature = async () => {
    try {
      const res = await fetch('https://1c-tg-bot-deenfoool.amvera.io/api/nomenclature'); 
      if (!res.ok) throw new Error("Ошибка загрузки данных");
      const data = await res.json();
      setNomenclature(data);
      setCurrentPage(0);
    } catch (e) {
      alert(`❌ Ошибка: ${e.message}`);
    }
  };

  // Экранирование специальных символов
  const escapeHtml = (text) => {
    return text.replace(/&/g, '&amp;')
               .replace(/</g, '<')
               .replace(/>/g, '>');
  };

  // Добавление новой записи
  const handleAddItem = async (e) => {
    e.preventDefault();
    const { code, name } = newItem;
    if (!code || !name) {
      alert("❌ Заполните все поля.");
      return;
    }

    if (code.length < 5 || isNaN(code)) {
      alert("❌ Код должен быть минимум 5 цифрами.");
      return;
    }

    const existing = nomenclature.find(item => item.code === code);
    if (existing) {
      alert("❌ Такой код уже существует.");
      return;
    }

    try {
      const res = await fetch('https://1c-tg-bot-deenfoool.amvera.io/api/add',  {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, name })
      });

      if (res.ok) {
        setNomenclature([...nomenclature, { code, name }]);
        setNewItem({ code: '', name: '' });
        alert("✅ Запись добавлена.");
      } else {
        alert("❌ Не удалось добавить запись.");
      }
    } catch (e) {
      alert(`❌ Ошибка: ${e.message}`);
    }
  };

  // Удаление записи
  const handleDeleteItem = async (code) => {
    try {
      const res = await fetch(`https://1c-tg-bot-deenfoool.amvera.io/api/delete/${code}`,  {
        method: 'DELETE'
      });

      if (res.ok) {
        setNomenclature(nomenclature.filter(item => item.code !== code));
        alert("✅ Запись удалена.");
      } else {
        alert("❌ Не удалось удалить запись.");
      }
    } catch (e) {
      alert(`❌ Ошибка: ${e.message}`);
    }
  };

  // Импорт из .txt
  const handleImportFile = async (e) => {
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

        try {
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
        } catch (e) {
          alert(`❌ Ошибка: ${e.message}`);
        }
      };

      reader.readAsText(file);
    };

    fileInput.click();
  };

  // Поиск
  const filteredItems = nomenclature.filter(item =>
    item.code.includes(searchQuery) || item.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Пагинация
  const totalPages = Math.ceil(filteredItems.length / ITEMS_PER_PAGE);
  const currentItems = filteredItems.slice(
    currentPage * ITEMS_PER_PAGE,
    (currentPage + 1) * ITEMS_PER_PAGE
  );

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Header */}
      <header className="bg-white shadow-md py-4 px-6 flex justify-between items-center border-b border-gray-200">
        <h1 className="text-xl md:text-2xl font-bold text-gray-800">Telegram Mini App</h1>
        <nav className="flex space-x-4">
          <button
            onClick={() => setActiveTab('list')}
            className={`px-4 py-2 rounded-md ${
              activeTab === 'list'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Список
          </button>
          <button
            onClick={fetchNomenclature}
            className="px-4 py-2 rounded-md bg-gray-200 text-gray-700 hover:bg-gray-300"
          >
            Обновить
          </button>
        </nav>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 max-w-5xl">
        {activeTab === 'list' && (
          <>
            {/* Search and Controls */}
            <div className="mb-6 flex flex-col sm:flex-row gap-4">
              <input
                type="text"
                placeholder="Поиск по коду или наименованию..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full sm:w-64 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <label className="w-full sm:w-48 flex items-center justify-center">
                <span className="cursor-pointer inline-block w-full text-center px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors" onClick={handleImportFile}>
                  Импорт .txt
                </span>
              </label>
            </div>

            {/* Table of Items */}
            <div className="bg-white shadow-md rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-100">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      #
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Код
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Наименование
                    </th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Действие
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {currentItems.length > 0 ? (
                    currentItems.map((item) => (
                      <tr key={item.code} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.code}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{escapeHtml(item.name)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"></td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleDeleteItem(item.code)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Удалить
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="px-6 py-4 text-center text-sm text-gray-500">
                        Ничего не найдено
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="mt-4 flex justify-between items-center">
              <button
                disabled={currentPage === 0}
                onClick={() => setCurrentPage(currentPage - 1)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50"
              >
                Предыдущая
              </button>
              <span>Страница {currentPage + 1} из {totalPages}</span>
              <button
                disabled={currentPage >= totalPages - 1}
                onClick={() => setCurrentPage(currentPage + 1)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50"
              >
                Следующая
              </button>
            </div>

            {/* Add New Item Form */}
            <div className="mt-8 bg-white shadow-md rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4 text-gray-800">Добавить новую позицию</h2>
              <form onSubmit={handleAddItem}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Код (5+ символов)"
                    value={newItem.code}
                    onChange={(e) => setNewItem({ ...newItem, code: e.target.value })}
                    className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    placeholder="Наименование"
                    value={newItem.name}
                    onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                    className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <button
                  type="submit"
                  className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Добавить
                </button>
              </form>
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white mt-8 py-4 border-t border-gray-200 text-center text-gray-500 text-sm">
        © {new Date().getFullYear()} Telegram Mini App
      </footer>
    </div>
  );
};

export default App;