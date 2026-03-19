// Tema
const toggleBtn = document.getElementById('toggle-theme');
const html = document.documentElement;

function setTheme(isDark) {
  html.setAttribute('data-theme', isDark ? 'dark' : 'light');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
  setTheme(savedTheme === 'dark');
} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
  setTheme(true);
}

toggleBtn.addEventListener('click', () => {
  const isDark = html.getAttribute('data-theme') !== 'dark';
  setTheme(isDark);
  toggleBtn.innerHTML = `<i class="fa-solid fa-${isDark ? 'sun' : 'moon'}"></i>`;
});

// Tarefas
const form = document.getElementById('task-form');
const input = document.getElementById('task-input');
const list = document.getElementById('task-list');
const totalEl = document.getElementById('total');
const pendingEl = document.getElementById('pending');

let tasks = JSON.parse(localStorage.getItem('tasks')) || [];

function saveTasks() {
  localStorage.setItem('tasks', JSON.stringify(tasks));
  updateStats();
}

function renderTasks() {
  list.innerHTML = '';
  tasks.forEach((task, index) => {
    const li = document.createElement('li');
    li.className = task.done ? 'completed' : '';
    li.innerHTML = `
      <span>${task.text}</span>
      <div class="actions">
        <button class="toggle" data-index="${index}">
          <i class="fa-solid fa-${task.done ? 'rotate-left' : 'check'}"></i>
        </button>
        <button class="delete" data-index="${index}">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    `;
    list.appendChild(li);
  });
}

function updateStats() {
  const total = tasks.length;
  const pending = tasks.filter(t => !t.done).length;
  totalEl.textContent = `${total} tarefa${total !== 1 ? 's' : ''}`;
  pendingEl.textContent = `${pending} pendente${pending !== 1 ? 's' : ''}`;
}

form.addEventListener('submit', e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  
  tasks.push({ text, done: false });
  saveTasks();
  renderTasks();
  input.value = '';
  input.focus();
});

list.addEventListener('click', e => {
  const btn = e.target.closest('button');
  if (!btn) return;
  
  const index = parseInt(btn.dataset.index);
  
  if (btn.classList.contains('toggle')) {
    tasks[index].done = !tasks[index].done;
  } else if (btn.classList.contains('delete')) {
    if (confirm('Remover esta tarefa?')) {
      tasks.splice(index, 1);
    }
  }
  
  saveTasks();
  renderTasks();
});

// Inicialização
renderTasks();
updateStats();

// Registrar Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => console.log('Service Worker registrado', reg))
      .catch(err => console.log('Falha ao registrar SW', err));
  });
}
