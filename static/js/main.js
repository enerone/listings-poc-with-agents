// Main JavaScript file for Amazon Listings Generator

// Global utilities
window.utils = {
    // Show loading state
    showLoading: function(element) {
        if (element) {
            element.classList.add('loading');
        }
    },

    // Hide loading state
    hideLoading: function(element) {
        if (element) {
            element.classList.remove('loading');
        }
    },

    // Show alert message
    showAlert: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" style="float: right; background: none; border: none; cursor: pointer;">&times;</button>
        `;
        
        // Insert at the top of the main content
        const mainContent = document.querySelector('.main-content .container');
        if (mainContent) {
            mainContent.insertBefore(alertDiv, mainContent.firstChild);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentElement) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    },

    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Validate image file
    validateImageFile: function(file) {
        const validTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (!validTypes.includes(file.type)) {
            return { valid: false, error: 'Tipo de archivo no válido. Solo PNG, JPG, JPEG, GIF, WEBP.' };
        }

        if (file.size > maxSize) {
            return { valid: false, error: 'Archivo demasiado grande. Máximo 5MB.' };
        }

        return { valid: true };
    },

    // API request helper
    apiRequest: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }
};

// Initialize tooltips and other UI components
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add loading states to buttons
    document.querySelectorAll('button[type="submit"], .btn-submit').forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && !this.form.checkValidity()) {
                return;
            }
            
            const originalText = this.innerHTML;
            this.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; display: inline-block; margin-right: 8px;"></div> Procesando...';
            this.disabled = true;
            
            // Reset after 30 seconds if not handled by form
            setTimeout(() => {
                if (this.disabled) {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }
            }, 30000);
        });
    });

    // Add click outside to close dropdowns
    document.addEventListener('click', function(e) {
        document.querySelectorAll('.dropdown.open').forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });
    });

    // Image lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save (if in form)
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            e.preventDefault();
            const submitBtn = activeForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(modal => {
            if (modal.style.display !== 'none') {
                modal.style.display = 'none';
            }
        });
    }
});

// Error handling for images
document.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        e.target.src = '/static/images/placeholder.png';
        e.target.alt = 'Imagen no disponible';
    }
}, true);

// Performance monitoring
if (window.performance && window.performance.mark) {
    window.addEventListener('load', function() {
        window.performance.mark('page-load-complete');
        
        // Log performance metrics
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
            console.log('Page Load Performance:', {
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                totalTime: navigation.loadEventEnd - navigation.fetchStart
            });
        }
    });
}