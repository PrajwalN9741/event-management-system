document.addEventListener('DOMContentLoaded', function() {
    const editItemModal = document.getElementById('editItemModal');
    if (editItemModal) {
        editItemModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');
            const category = button.getAttribute('data-category');
            const unit = button.getAttribute('data-unit');
            const quantity = button.getAttribute('data-quantity');
            const price = button.getAttribute('data-price');
            const threshold = button.getAttribute('data-threshold');

            const form = editItemModal.querySelector('#editItemForm');
            form.action = `/inventory/${id}/edit`;

            editItemModal.querySelector('#edit_name').value = name;
            editItemModal.querySelector('#edit_category').value = category;
            editItemModal.querySelector('#edit_unit').value = unit;
            editItemModal.querySelector('#edit_quantity').value = quantity;
            editItemModal.querySelector('#edit_price').value = price;
            editItemModal.querySelector('#edit_threshold').value = threshold;
        });
    }
});
