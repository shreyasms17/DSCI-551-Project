function handleImageError(imageElement) {
    // Find the parent row of the image and remove it from the table
    var productRow = imageElement.closest('.product-row');
    productRow.remove();
}
