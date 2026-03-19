const lista = document.getElementById("lista");

function salvar() {
 const input = document.getElementById("input");
 const valor = input.value;

 if (!valor) return;

 let itens = JSON.parse(localStorage.getItem("itens")) || [];
 itens.push(valor);

 localStorage.setItem("itens", JSON.stringify(itens));

 input.value = "";
 carregar();
}

function carregar() {
 lista.innerHTML = "";
 let itens = JSON.parse(localStorage.getItem("itens")) || [];

 itens.forEach(item => {
   const li = document.createElement("li");
   li.textContent = item;
   lista.appendChild(li);
 });
}

carregar();
