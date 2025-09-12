// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initTypeWriter();
    initSmoothScrolling();
    initNavbarScroll();
    initBackToTop();
    initMobileMenu();
    initFloatingImage();
    initCardHoverEffects();
    initFormSubmission();
    initAnimations();
    initFlowerAnimation();
});

// Typewriter Effect
function initTypeWriter() {
    const typewriterElement = document.querySelector('.typewriter');
    if (typewriterElement) {
        typeWriter(typewriterElement);
    }
}

function typeWriter(element) {
    const text = element.getAttribute('data-text');
    let i = 0;
    const speed = 50;
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        } else {
            element.classList.add('typing-complete');
        }
    }
    
    element.textContent = '';
    type();
}

// Smooth Scrolling
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                const navLinks = document.querySelector('.nav-links');
                const hamburger = document.querySelector('.hamburger');
                if (navLinks && hamburger) {
                    navLinks.classList.remove('active');
                    hamburger.classList.remove('active');
                    document.body.style.overflow = '';
                }
            }
        });
    });
}

// Navbar Scroll Effect
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        // Navbar background on scroll
        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Hide/show navbar on scroll
        if (currentScroll <= 0) {
            navbar.classList.remove('scroll-up');
            return;
        }
        
        if (currentScroll > lastScroll && !navbar.classList.contains('scroll-down')) {
            // Scroll Down
            navbar.classList.remove('scroll-up');
            navbar.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && navbar.classList.contains('scroll-down')) {
            // Scroll Up
            navbar.classList.remove('scroll-down');
            navbar.classList.add('scroll-up');
        }
        
        lastScroll = currentScroll;
    });
}

// Back to Top Button
function initBackToTop() {
    const backToTopButton = document.getElementById('back-to-top');
    if (!backToTopButton) return;
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    });

    backToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Mobile Menu Toggle
function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (!hamburger || !navLinks) return;
    
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
        
        if (navLinks.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    });

    // Close mobile menu when clicking on a link
    const navItems = document.querySelectorAll('.nav-links a');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navLinks.classList.remove('active');
            hamburger.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
}

// Floating Image Animation
function initFloatingImage() {
    const floatingImage = document.getElementById('floatingImage');
    const cards = document.querySelectorAll('.card');
    
    if (!floatingImage || cards.length === 0) return;
    
    let currentCardIndex = 0;
    let isAnimating = false;

    function moveFloatingImage() {
        if (isAnimating) return;
        
        const nextCardIndex = (currentCardIndex + 1) % cards.length;
        const currentCard = cards[currentCardIndex];
        const nextCard = cards[nextCardIndex];
        
        if (!currentCard || !nextCard) return;
        
        isAnimating = true;
        
        // Get positions
        const currentRect = currentCard.getBoundingClientRect();
        const nextRect = nextCard.getBoundingClientRect();
        
        // Calculate center positions
        const currentX = currentRect.left + currentRect.width / 2 - 75;
        const currentY = currentRect.top + window.scrollY - 100;
        const nextX = nextRect.left + nextRect.width / 2 - 75;
        const nextY = nextRect.top + window.scrollY - 100;
        
        // Set initial position
        floatingImage.style.left = `${currentX}px`;
        floatingImage.style.top = `${currentY}px`;
        floatingImage.style.opacity = '0.8';
        
        // Animate to next position
        floatingImage.style.transition = 'all 1.5s cubic-bezier(0.68, -0.55, 0.27, 1.55)';
        
        // Add a small delay before starting the animation
        setTimeout(() => {
            floatingImage.style.left = `${nextX}px`;
            floatingImage.style.top = `${nextY}px`;
            
            // Update current card index after animation completes
            setTimeout(() => {
                currentCardIndex = nextCardIndex;
                isAnimating = false;
            }, 1500);
        }, 100);
    }

    // Initialize floating image position
    function initFloatingImagePosition() {
        const firstCard = cards[0];
        if (firstCard) {
            const firstRect = firstCard.getBoundingClientRect();
            floatingImage.style.left = `${firstRect.left + firstRect.width / 2 - 75}px`;
            floatingImage.style.top = `${firstRect.top + window.scrollY - 100}px`;
            floatingImage.style.opacity = '0.8';
        }
        
        // Move the image every 3 seconds
        setInterval(moveFloatingImage, 3000);
    }

    // Initialize on window load
    window.addEventListener('load', initFloatingImagePosition);
}

// Card Hover Effects
function initCardHoverEffects() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-10px) scale(1.02)';
            card.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
            card.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.1)';
        });
    });
}

// Form Submission
function initFormSubmission() {
    const contactForm = document.querySelector('.contact-form');
    if (!contactForm) return;
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const formObject = {};
        formData.forEach((value, key) => {
            formObject[key] = value;
        });
        
        // Here you would typically send the form data to a server
        console.log('Form submitted:', formObject);
        
        // Show success message with animation
        const successMessage = document.createElement('div');
        successMessage.className = 'success-message';
        successMessage.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>شكراً لتواصلك معنا! سنرد عليك في أقرب وقت ممكن.</span>
        `;
        
        this.appendChild(successMessage);
        
        // Remove success message after 5 seconds
        setTimeout(() => {
            successMessage.style.opacity = '0';
            setTimeout(() => {
                successMessage.remove();
            }, 500);
        }, 5000);
        
        this.reset();
    });
}

// Animations
function initAnimations() {
    // Add animation class to elements that should animate on scroll
    const animateElements = document.querySelectorAll('section, .skill-level, .card, .section-title');
    animateElements.forEach((element, index) => {
        element.classList.add('animate-on-scroll');
        element.style.transitionDelay = `${index * 0.1}s`;
    });
    
    // Initialize skill bars
    const skillLevels = document.querySelectorAll('.skill-level');
    skillLevels.forEach(level => {
        const width = level.getAttribute('data-level');
        level.style.width = '0';
        level.setAttribute('data-level', width);
    });
    
    // Animate on scroll
    function animateOnScroll() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight - 50) {
                element.classList.add('visible');
                
                // Animate skill bars
                if (element.classList.contains('skill-level')) {
                    const width = element.getAttribute('data-level');
                    element.style.width = width;
                }
            }
        });
        
        // Animate hero section elements
        const heroContent = document.querySelector('.hero-content');
        if (heroContent) {
            const heroContentTop = heroContent.getBoundingClientRect().top;
            if (heroContentTop < window.innerHeight - 100) {
                heroContent.classList.add('animate');
            }
        }
    }
    
    // Initial check for elements in viewport
    animateOnScroll();
    
    // Add scroll event listener for animations
    window.addEventListener('scroll', animateOnScroll);
    
    // Trigger scroll to update navbar on page load
    window.dispatchEvent(new Event('scroll'));
    
    // Handle page load animation
    document.body.style.opacity = '1';
    document.body.classList.add('loaded');
    
    // Animate hero content
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        setTimeout(() => {
            heroContent.classList.add('animate');
        }, 500);
    }
}

// Flower Animation
function initFlowerAnimation() {
    const flowerSection = document.getElementById('flower-section');
    if (!flowerSection) return;
    
    let flowerShown = false;

    function checkScroll() {
        // Check if we've scrolled to the bottom of the page
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
            if (!flowerShown) {
                flowerSection.classList.remove('d-none');
                // Small delay to allow the display property to take effect
                setTimeout(() => {
                    flowerSection.classList.add('visible');
                    flowerShown = true;
                }, 50);
            }
        } else if (flowerShown) {
            flowerSection.classList.remove('visible');
            // Only hide completely if scrolled up significantly
            if (window.scrollY < document.body.offsetHeight - window.innerHeight * 1.5) {
                setTimeout(() => {
                    if (!flowerSection.classList.contains('visible')) {
                        flowerSection.classList.add('d-none');
                    }
                }, 500);
                flowerShown = false;
            }
        }
    }

    // Add scroll event listener
    window.addEventListener('scroll', checkScroll);

    // Initial check in case page loads at the bottom
    checkScroll();
}
