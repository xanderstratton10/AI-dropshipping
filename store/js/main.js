document.addEventListener('DOMContentLoaded', () => {
    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-question');
    faqItems.forEach(item => {
        item.addEventListener('click', () => {
            const answer = item.nextElementSibling;
            const isOpen = answer.style.display === 'block';
            
            // Close all other answers
            document.querySelectorAll('.faq-answer').forEach(ans => ans.style.display = 'none');
            
            // Toggle current answer
            answer.style.display = isOpen ? 'none' : 'block';
        });
    });

    // Countdown Timer (HH:MM:SS)
    const countdownElement = document.getElementById('timer');
    if (countdownElement) {
        let timeLeft = 2 * 60 * 60 + 45 * 60 + 30; // 2h 45m 30s
        
        const updateTimer = () => {
            const hours = Math.floor(timeLeft / 3600);
            const minutes = Math.floor((timeLeft % 3600) / 60);
            const seconds = timeLeft % 60;
            
            countdownElement.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            
            if (timeLeft > 0) {
                timeLeft--;
            } else {
                clearInterval(timerInterval);
                countdownElement.textContent = "SALE ENDED";
            }
        };
        
        const timerInterval = setInterval(updateTimer, 1000);
        updateTimer();
    }

    // Email Popup
    const popup = document.getElementById('email-popup');
    if (popup) {
        setTimeout(() => {
            if (!localStorage.getItem('popupShown')) {
                popup.style.display = 'flex';
            }
        }, 5000); // Show after 5 seconds

        const closeBtn = popup.querySelector('.close-popup');
        closeBtn.addEventListener('click', () => {
            popup.style.display = 'none';
            localStorage.setItem('popupShown', 'true');
        });
    }

    // Add to Cart Simulation
    const addToCartBtn = document.getElementById('add-to-cart');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', () => {
            const originalText = addToCartBtn.textContent;
            addToCartBtn.textContent = 'Adding...';
            addToCartBtn.disabled = true;
            
            setTimeout(() => {
                addToCartBtn.textContent = 'Added to Cart!';
                addToCartBtn.style.backgroundColor = '#4caf50';
                
                // Update cart count
                const cartCount = document.querySelector('.cart-count');
                cartCount.textContent = parseInt(cartCount.textContent) + 1;
                
                setTimeout(() => {
                    addToCartBtn.textContent = originalText;
                    addToCartBtn.style.backgroundColor = '';
                    addToCartBtn.disabled = false;
                }, 2000);
            }, 1000);
        });
    }
});
