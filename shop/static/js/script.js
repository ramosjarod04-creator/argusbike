// Auto-dismiss messages
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Form validation
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const inputs = this.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.style.borderColor = '#ef4444';
            } else {
                input.style.borderColor = '';
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            alert('Please fill in all required fields.');
        }
    });
});

// Stock quantity validation
const quantityInputs = document.querySelectorAll('input[name="quantity"]');
quantityInputs.forEach(input => {
    input.addEventListener('input', function() {
        if (this.value < 0) {
            this.value = 0;
        }
    });
});

// Price calculation preview
const saleForm = document.querySelector('.sale-form');
if (saleForm) {
    const productSelect = saleForm.querySelector('select[name="product"]');
    const quantityInput = saleForm.querySelector('input[name="quantity"]');
    const discountInput = saleForm.querySelector('input[name="discount"]');
    
    function updateTotal() {
        // This would need actual product price data
        // For now, just validate quantities
        if (quantityInput && quantityInput.value < 1) {
            quantityInput.value = 1;
        }
        
        if (discountInput && discountInput.value < 0) {
            discountInput.value = 0;
        }
    }
    
    if (quantityInput) quantityInput.addEventListener('input', updateTotal);
    if (discountInput) discountInput.addEventListener('input', updateTotal);
}

console.log('🚴 Argus Bike Shop System Ready!');