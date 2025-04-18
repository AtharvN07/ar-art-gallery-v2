function addToCart(id) {
    fetch('/add_to_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    }).then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById('cart-count').innerText = data.cart.length;
    });
}
function removeFromCart(id) {
    fetch('/remove_from_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    }).then(response => response.json())
    .then(data => {
        alert(data.message);
        location.reload();  // Refresh the cart page
    });
}

