/* Shopping Cart */
const usernameElement = document.getElementById('username');
const username = usernameElement.getAttribute('data-username');


// Genera una clave única para el almacenamiento local
const userStorageKey = `user_cart_${username}`;

// Verificar si hay datos de carrito en el Local Storage al cargar la página
window.addEventListener('load', () => {
    if (localStorage.getItem(userStorageKey)) {
        buyThings = JSON.parse(localStorage.getItem(userStorageKey));
        totalCard = parseFloat(localStorage.getItem('total')) || 0;
        countProduct = parseInt(localStorage.getItem('count')) || 0;
        loadHtml();
    }
});


//variables
let allContainerCart = document.querySelector('.products');
let containerBuyCart = document.querySelector('.card-items');
let priceTotal = document.querySelector('.price-total')
let amountProduct = document.querySelector('.count-product');


let buyThings = [];
let totalCard = 0;
let countProduct = 0;

//functions
loadEventListenrs();
function loadEventListenrs(){
    allContainerCart.addEventListener('click', addProduct);

    containerBuyCart.addEventListener('click', deleteProduct);
}

function addProduct(e){
    e.preventDefault();
    if (e.target.classList.contains('btn-add-cart')) {
        const selectProduct = e.target.parentElement; 
        readTheContent(selectProduct);
    }
}

function deleteProduct(e) {
    if (e.target.classList.contains('delete-product')) {
        const deleteId = e.target.getAttribute('data-id');

        buyThings.forEach(value => {
            if (value.id == deleteId) {
                let priceReduce = parseFloat(value.price) * parseFloat(value.amount);
                totalCard = totalCard - priceReduce;
                totalCard = totalCard.toFixed(2);
                countProduct--; // Disminuye el contador al eliminar un producto
            }
        });

        // Asegúrate de que countProduct nunca sea negativo
        countProduct = Math.max(countProduct, 0);

        buyThings = buyThings.filter(product => product.id !== deleteId);
    }

    if (buyThings.length === 0) {
        priceTotal.innerHTML = 0;
        amountProduct.innerHTML = 0;
    }

    // Actualiza el HTML después de eliminar un producto
    loadHtml();
}


function readTheContent(product){
    const infoProduct = {
        image: product.querySelector('div img').src,
        title: product.querySelector('.title').textContent,
        price: product.querySelector('div p span').textContent,
        id: product.querySelector('a').getAttribute('data-id'),
        amount: 1
    }

    totalCard = parseFloat(totalCard) + parseFloat(infoProduct.price);
    totalCard = totalCard.toFixed(2);

    const exist = buyThings.some(product => product.id === infoProduct.id);
    if (exist) {
        const pro = buyThings.map(product => {
            if (product.id === infoProduct.id) {
                product.amount++;
                return product;
            } else {
                return product
            }
        });
        buyThings = [...pro];
    } else {
        buyThings = [...buyThings, infoProduct]
        countProduct++;
    }
    loadHtml();
}


// rendiriza la ventana agregando nuevas clases DOM
function loadHtml(){
    clearHtml();
    buyThings.forEach(product => {
        const {image, title, price, amount, id} = product;
        const row = document.createElement('div');
        row.classList.add('item');
        row.innerHTML = `
        <img src="${image}" alt="">
        <div class="item-content">
            <h5>${title}</h5>
            <h5 class="cart-price">${price}bs</h5>
            <h6>cantidad: ${amount}</h6>
        </div>
        <span class="delete-product" data-id="${id}">X</span>
        `;

        containerBuyCart.appendChild(row);

        priceTotal.innerHTML = totalCard;

        amountProduct.innerHTML = countProduct;
    });

    const username = "{{ user }}";

     // Guarda el carrito en el Local Storage
     localStorage.setItem(userStorageKey, JSON.stringify(buyThings));
     localStorage.setItem('total', totalCard);
     localStorage.setItem('count', countProduct);

}


 function clearHtml(){
    containerBuyCart.innerHTML = '';
 }

 // Agregar event listeners para los botones "-" y "+"
allContainerCart.addEventListener('click', (e) => {
    if (e.target.classList.contains('quantity-increase')) {
        const increaseId = e.target.getAttribute('data-id');
        updateQuantity(increaseId, 1); // Incrementar la cantidad en 1
    } else if (e.target.classList.contains('quantity-decrease')) {
        const decreaseId = e.target.getAttribute('data-id');
        updateQuantity(decreaseId, -1); // Disminuir la cantidad en 1
    }
});

// ...

// Función para actualizar la cantidad de un producto en el carrito
function updateQuantity(productId, change) {
    buyThings.forEach((product) => {
        if (product.id == productId) {
            const newAmount = product.amount + change;
            if (newAmount >= 1) {
                product.amount = newAmount;
                updateLocalStorage();
                updateTotal(); // Actualiza el total después de cambiar la cantidad
                loadHtml();
            }
        }
    });
}

// Función para calcular el total de la compra
function updateTotal() {
    totalCard = buyThings.reduce((total, product) => {
        return total + parseFloat(product.price) * product.amount;
    }, 0);

    totalCard = totalCard.toFixed(2);
    priceTotal.innerHTML = totalCard;
}



// Actualiza el Local Storage después de cambiar la cantidad
function updateLocalStorage() {
    localStorage.setItem(userStorageKey, JSON.stringify(buyThings));
    // Después de actualizar totalCard
}

function finalizarCompra(event) {
    event.preventDefault(); // Evitar que el formulario se envíe automáticamente

    const productsToBuy = buyThings;

    // Verificar si el carrito está vacío
    if (productsToBuy.length === 0){
        alert('El carrito está vacío. Agrega productos antes de finalizar la compra.');
        return; // No proceder con la compra
    }

    // El carrito tiene productos, procede con la compra
    const productsInput = document.getElementById('products-input');
    productsInput.value = JSON.stringify(productsToBuy);

    // Enviar los datos al servidor Flask
    fetch('/comprar', {
        method: 'POST',
        body: new FormData(document.getElementById('checkout-form'))
    })
    .then(response => {
        if (response.ok) {
            // Manejar la respuesta del servidor, por ejemplo, redirigir a una página de confirmación.

            window.location.href = '/checkout';

        } else {
            // Manejar errores, por ejemplo, mostrar un mensaje de error.
            console.error('Error al finalizar la compra');
        }
    })
    .catch(error => {
        console.error('Error al finalizar la compra:', error);
    });

    localStorage.removeItem(userStorageKey);



}

// DOM DOM DOM
const buttonFinalizarCompra = document.querySelector('.button-buy');
buttonFinalizarCompra.addEventListener('click', finalizarCompra);