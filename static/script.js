const API_URL = 'http://localhost:8000';
let limit = 20;
let loading = false;
let hasMore = true;
let products = [];
let cart = JSON.parse(localStorage.getItem('cart')) || [];

const grid = document.getElementById('grid');
const searchInput = document.getElementById('search');
const categorySelect = document.getElementById('category');
const cartCount = document.getElementById('cart-count');

/* ===== API ===== */
async function loadProducts() {
  if (loading || !hasMore) return;
  loading = true;



  const search = searchInput.value;
  const category =
    categorySelect.value !== 'all' ? categorySelect.value : '';

  const res = await fetch(
    `${API_URL}/products?&limit=${limit}&search=${search}&category=${category}`
  );

  const data = await res.json();

  renderProducts(data);

  limit += 20;
  loading = false;
}

/* ===== UI ===== */
function renderProducts(list) {
  grid.innerHTML = '';

  if (!list.length) {
    grid.innerHTML = '<p>Товары не найдены</p>';
    return;
  }

  list.forEach(p => {
    grid.insertAdjacentHTML('beforeend', `
      <div class="card">
        <div class="card-body">
          <h3>${p.title}</h3>
          <div class="price">${p.price} ₽</div>
        </div>
        <button data-id="${p.id}">В корзину</button>
      </div>
    `);
  });
}
window.addEventListener('scroll', () => {
  const scrollBottom =
    window.innerHeight + window.scrollY >=
    document.documentElement.scrollHeight - 300;

  if (scrollBottom) {
    loadProducts();
  }
});

function onFilterChange() {
  limit = 20;
  loadProducts(true);
}

searchInput.addEventListener('input', onFilterChange);
categorySelect.addEventListener('change', onFilterChange);

/* ===== Категории ===== */
function initCategories() {
  const cats = ['all', ...new Set(products.map(p => p.category))];
  categorySelect.innerHTML = cats
    .map(c => `<option value="${c}">${c}</option>`)
    .join('');
}

/* ===== Фильтры ===== */
function applyFilters() {
  const q = searchInput.value.toLowerCase();
  const cat = categorySelect.value;
  limit = 20;

  const filtered = products.filter(p =>
    p.title.toLowerCase().includes(q) &&
    (cat === 'all' || p.category === cat)
  );
  renderProducts(filtered);
}

/* ===== Корзина ===== */
document.addEventListener('click', e => {
  if (e.target.dataset.id) {
    cart.push(Number(e.target.dataset.id));
    localStorage.setItem('cart', JSON.stringify(cart));
    cartCount.textContent = cart.length;
  }
});

searchInput.addEventListener('input', applyFilters);
categorySelect.addEventListener('change', applyFilters);

cartCount.textContent = cart.length;
loadProducts();
