function addToCart(productId) {
    fetch('/cart', {
        method: 'POST',
        body: new URLSearchParams({ product_id: productId }),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).then(() => alert("Product added to cart!"));
}
