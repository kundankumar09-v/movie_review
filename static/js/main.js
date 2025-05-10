// Main JavaScript file for MovieCritic application with enhanced animations and interactions

document.addEventListener('DOMContentLoaded', function() {
    setupFlashMessages();
    setupShareFunctionality();
    initRatingSelector();
    scrollToReview();
    initAnimations();
    setupNavbarEffects();
    setupMovieCardEffects();
});

// Initialize animations for elements
function initAnimations() {
    // Stagger animation for movie cards
    const movieCards = document.querySelectorAll('.movie-card');
    if (movieCards.length) {
        movieCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
        });
    }

    // Apply entrance animations to page sections
    const pageSections = document.querySelectorAll('section, .card, .list-group-item');
    if (pageSections.length) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate__fadeInUp', 'animate__animated');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        pageSections.forEach(section => {
            observer.observe(section);
        });
    }
}

// Add interactive effects to the navbar
function setupNavbarEffects() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.classList.add('animate__pulse', 'animate__animated');
        });
        
        link.addEventListener('animationend', function() {
            this.classList.remove('animate__pulse', 'animate__animated');
        });
    });

    // Add shadow on scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 10) {
                navbar.classList.add('shadow-lg');
            } else {
                navbar.classList.remove('shadow-lg');
            }
        }
    });
}

// Add interactive effects to movie cards
function setupMovieCardEffects() {
    const cards = document.querySelectorAll('.movie-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const img = this.querySelector('.card-img-top');
            if (img) {
                img.style.transform = 'scale(1.05)';
            }
            
            const overlay = this.querySelector('.overlay');
            if (overlay) {
                overlay.style.opacity = '1';
                overlay.style.transform = 'translateY(0)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const img = this.querySelector('.card-img-top');
            if (img) {
                img.style.transform = '';
            }
            
            const overlay = this.querySelector('.overlay');
            if (overlay) {
                overlay.style.opacity = '';
                overlay.style.transform = '';
            }
        });
    });
}

// Auto-hide flash messages with animation
function setupFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.classList.add('animate__fadeOut');
            message.addEventListener('animationend', () => {
                message.style.display = 'none';
            });
        }, 5000);
    });
}

// Enhanced share functionality
function setupShareFunctionality() {
    const shareUrl = document.getElementById('shareUrl');
    const copyBtn = document.getElementById('copyBtn');
    
    if (shareUrl && copyBtn) {
        copyBtn.addEventListener('click', function() {
            shareUrl.select();
            shareUrl.setSelectionRange(0, 99999); // For mobile devices
            
            // Since navigator.clipboard requires HTTPS, we use this approach
            try {
                // Try the modern approach first
                if (navigator.clipboard && window.location.protocol === 'https:') {
                    navigator.clipboard.writeText(shareUrl.value)
                        .then(() => {
                            showCopyFeedback(copyBtn, true);
                        })
                        .catch(() => {
                            document.execCommand('copy'); // Fallback
                            showCopyFeedback(copyBtn, true);
                        });
                } else {
                    // Fallback to execCommand for HTTP
                    const successful = document.execCommand('copy');
                    showCopyFeedback(copyBtn, successful);
                }
            } catch (err) {
                // Show manual instructions more prominently
                showCopyFeedback(copyBtn, false);
            }
        });
    }
    
    function showCopyFeedback(button, success) {
        const originalHtml = button.innerHTML;
        
        if (success) {
            button.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
            button.classList.add('btn-success');
            button.classList.remove('btn-primary');
        } else {
            button.innerHTML = '<i class="fas fa-info me-1"></i> Select All';
        }
        
        setTimeout(() => {
            button.innerHTML = originalHtml;
            button.classList.remove('btn-success');
            button.classList.add('btn-primary');
        }, 2000);
    }
}

// Smooth scroll to review with highlight effect
function scrollToReview() {
    if (window.location.hash) {
        const reviewId = window.location.hash.substring(1);
        const reviewElement = document.getElementById(reviewId);
        
        if (reviewElement) {
            // Delay scroll to allow page to fully load
            setTimeout(() => {
                reviewElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // Add highlight effect
                reviewElement.classList.add('animate__animated', 'animate__flash');
                reviewElement.style.backgroundColor = 'rgba(102, 16, 242, 0.1)';
                
                // Remove highlight after animation
                reviewElement.addEventListener('animationend', () => {
                    reviewElement.classList.remove('animate__animated', 'animate__flash');
                    
                    // Fade out the background color
                    setTimeout(() => {
                        reviewElement.style.transition = 'background-color 1s ease';
                        reviewElement.style.backgroundColor = '';
                    }, 500);
                });
            }, 500);
        }
    }
}

// Enhanced rating selection for review form
function initRatingSelector() {
    const ratingStars = document.querySelectorAll('.rating-star');
    const ratingInput = document.getElementById('rating');
    const ratingText = document.querySelector('.rating-text');
    
    if (ratingStars.length && ratingInput) {
        const ratingDescriptions = [
            'Select a rating',
            'Terrible (1/10)',
            'Very Bad (2/10)',
            'Bad (3/10)',
            'Poor (4/10)',
            'Average (5/10)',
            'OK (6/10)',
            'Good (7/10)',
            'Very Good (8/10)',
            'Great (9/10)',
            'Masterpiece (10/10)'
        ];
        
        // Set initial state
        if (ratingInput.value) {
            updateStars(parseInt(ratingInput.value));
        }
        
        ratingStars.forEach(star => {
            // Hover effect
            star.addEventListener('mouseenter', function() {
                const rating = parseInt(this.dataset.rating);
                highlightStars(rating);
                
                if (ratingText) {
                    ratingText.textContent = ratingDescriptions[rating];
                }
            });
            
            // Hover out effect
            star.addEventListener('mouseleave', function() {
                const currentRating = parseInt(ratingInput.value) || 0;
                highlightStars(currentRating);
                
                if (ratingText) {
                    ratingText.textContent = currentRating > 0 ? 
                        ratingDescriptions[currentRating] : ratingDescriptions[0];
                }
            });
            
            // Click to set rating
            star.addEventListener('click', function() {
                const rating = parseInt(this.dataset.rating);
                ratingInput.value = rating;
                updateStars(rating);
                
                // Add animation effect on selection
                ratingStars.forEach(s => {
                    if (parseInt(s.dataset.rating) <= rating) {
                        s.classList.add('animate__animated', 'animate__bounceIn');
                        s.addEventListener('animationend', () => {
                            s.classList.remove('animate__animated', 'animate__bounceIn');
                        }, { once: true });
                    }
                });
            });
        });
        
        function highlightStars(rating) {
            ratingStars.forEach(star => {
                const starValue = parseInt(star.dataset.rating);
                if (starValue <= rating) {
                    star.classList.add('active', 'fas', 'fa-star');
                    star.classList.remove('fa-star-o');
                } else {
                    star.classList.remove('active', 'fas', 'fa-star');
                    star.classList.add('fa-star-o');
                }
            });
        }
        
        function updateStars(rating) {
            highlightStars(rating);
            if (ratingText) {
                ratingText.textContent = ratingDescriptions[rating];
            }
        }
    }
}

// Add sample data with improved feedback
function initSampleData() {
    if (confirm('This will add sample movies and reviews to the database. Continue?')) {
        // Show loading state
        const loadingOverlay = document.createElement('div');
        loadingOverlay.style.position = 'fixed';
        loadingOverlay.style.top = '0';
        loadingOverlay.style.left = '0';
        loadingOverlay.style.width = '100%';
        loadingOverlay.style.height = '100%';
        loadingOverlay.style.backgroundColor = 'rgba(0,0,0,0.7)';
        loadingOverlay.style.display = 'flex';
        loadingOverlay.style.justifyContent = 'center';
        loadingOverlay.style.alignItems = 'center';
        loadingOverlay.style.zIndex = '9999';
        loadingOverlay.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h4 class="text-white">Adding sample data...</h4>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
        
        fetch('/add-sample-data', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                document.body.removeChild(loadingOverlay);
                if (data.success) {
                    const successOverlay = document.createElement('div');
                    successOverlay.style.position = 'fixed';
                    successOverlay.style.top = '0';
                    successOverlay.style.left = '0';
                    successOverlay.style.width = '100%';
                    successOverlay.style.height = '100%';
                    successOverlay.style.backgroundColor = 'rgba(0,0,0,0.7)';
                    successOverlay.style.display = 'flex';
                    successOverlay.style.justifyContent = 'center';
                    successOverlay.style.alignItems = 'center';
                    successOverlay.style.zIndex = '9999';
                    successOverlay.innerHTML = `
                        <div class="text-center animate__animated animate__fadeInUp">
                            <div class="mb-3">
                                <i class="fas fa-check-circle text-success" style="font-size: 4rem;"></i>
                            </div>
                            <h4 class="text-white mb-3">Sample data added successfully!</h4>
                            <p class="text-white mb-4">Refreshing page in 2 seconds...</p>
                            <div class="progress" style="height: 5px; width: 200px; margin: 0 auto;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated bg-success" 
                                     style="width: 0%;" id="refresh-progress"></div>
                            </div>
                        </div>
                    `;
                    document.body.appendChild(successOverlay);
                    
                    // Animate progress bar
                    const progressBar = document.getElementById('refresh-progress');
                    let width = 0;
                    const interval = setInterval(() => {
                        width += 2;
                        progressBar.style.width = `${width}%`;
                        if (width >= 100) {
                            clearInterval(interval);
                            window.location.reload();
                        }
                    }, 40); // 2000ms / 50 steps = 40ms per step
                } else {
                    alert('Error adding sample data: ' + data.error);
                }
            })
            .catch(error => {
                document.body.removeChild(loadingOverlay);
                console.error('Error:', error);
                alert('An error occurred while adding sample data.');
            });
    }
}