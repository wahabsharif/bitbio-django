/**
 * Header Navigation JavaScript
 * Simple CSS hover approach with mobile fallback
 */

document.addEventListener('DOMContentLoaded', function() {
  // Get all nav items
  const navItems = document.querySelectorAll('.nav-item.has-dropdown');
  const header = document.querySelector('.main-header');
  const overlay = document.querySelector('.dropdown-overlay');
  
  // Function to set dropdown position below header
  function setDropdownPosition() {
    if (header) {
      const headerHeight = header.offsetHeight;
      const dropdowns = document.querySelectorAll('.dropdown-menu');
      dropdowns.forEach(dropdown => {
        dropdown.style.top = headerHeight + 'px';
      });
    }
  }
  
  // Set initial position
  setDropdownPosition();
  
  // Update position on window resize
  window.addEventListener('resize', setDropdownPosition);
  
  // Function to show overlay
  function showOverlay() {
    if (overlay) {
      overlay.classList.add('active');
    }
    if (header) {
      header.classList.add('dropdown-active');
    }
  }
  
  // Function to hide overlay
  function hideOverlay() {
    if (overlay) {
      overlay.classList.remove('active');
    }
    if (header) {
      header.classList.remove('dropdown-active');
    }
  }
  
  // Simple function to close all dropdowns
  function closeAllDropdowns() {
    navItems.forEach(item => {
      item.classList.remove('active');
      item.classList.remove('keep-open');
    });
    hideOverlay();
  }
  
  // Desktop hover - show/hide overlay
  navItems.forEach(item => {
    item.addEventListener('mouseenter', function() {
      if (window.innerWidth > 992) {
        showOverlay();
      }
    });
    
    item.addEventListener('mouseleave', function() {
      if (window.innerWidth > 992) {
        // Use a small delay to prevent flickering when moving between menu items
        setTimeout(() => {
          const anyHovered = document.querySelector('.nav-item.has-dropdown:hover');
          if (!anyHovered) {
            hideOverlay();
          }
        }, 50);
      }
    });
  });
  
  // Desktop hover helper - keep dropdown open when hovering dropdown itself
  if (window.innerWidth > 992) {
    const dropdowns = document.querySelectorAll('.dropdown-menu');
    
    dropdowns.forEach(dropdown => {
      dropdown.addEventListener('mouseenter', function() {
        // Find the parent nav item and add a temporary class
        const navItem = document.querySelector('.nav-item.has-dropdown:hover');
        if (navItem) {
          navItem.classList.add('keep-open');
        }
        showOverlay();
      });
      
      dropdown.addEventListener('mouseleave', function() {
        // Remove the keep-open class
        const navItem = document.querySelector('.nav-item.has-dropdown.keep-open');
        if (navItem) {
          navItem.classList.remove('keep-open');
        }
        hideOverlay();
      });
    });
  }
  
  // Handle click on mobile for dropdown toggle
  navItems.forEach(item => {
    const link = item.querySelector('.nav-link');
    
    link.addEventListener('click', function(e) {
      // Only prevent default and toggle on mobile
      if (window.innerWidth <= 992) {
        e.preventDefault();
        
        // Close other open dropdowns
        navItems.forEach(otherItem => {
          if (otherItem !== item) {
            otherItem.classList.remove('active');
          }
        });
        
        // Toggle current dropdown
        const wasActive = item.classList.contains('active');
        item.classList.toggle('active');
        
        // Show/hide overlay based on dropdown state
        if (!wasActive) {
          showOverlay();
        } else {
          hideOverlay();
        }
      }
    });
  });

  // Click overlay to close dropdowns
  if (overlay) {
    overlay.addEventListener('click', function() {
      closeAllDropdowns();
    });
  }

  // Close dropdowns when clicking outside (mobile only)
  document.addEventListener('click', function(e) {
    if (window.innerWidth <= 992 && !e.target.closest('.nav-item')) {
      closeAllDropdowns();
    }
  });

  // Handle window resize - remove active class when switching to desktop
  let resizeTimer;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
      if (window.innerWidth > 992) {
        closeAllDropdowns();
      }
    }, 250);
  });

  // Keyboard navigation support
  document.addEventListener('keydown', function(e) {
    // ESC key closes all dropdowns
    if (e.key === 'Escape') {
      closeAllDropdowns();
    }
  });

  // Add aria-expanded attribute for accessibility
  navItems.forEach(item => {
    const link = item.querySelector('.nav-link');
    const dropdown = item.querySelector('.dropdown-menu');
    
    if (link && dropdown) {
      link.setAttribute('aria-haspopup', 'true');
      link.setAttribute('aria-expanded', 'false');
      
      // Update aria-expanded on mobile click
      link.addEventListener('click', function() {
        if (window.innerWidth <= 992) {
          const isExpanded = link.getAttribute('aria-expanded') === 'true';
          link.setAttribute('aria-expanded', !isExpanded);
        }
      });
    }
  });

  // Smooth scroll for anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
  anchorLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);
      
      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
});

// Optional: Add loading animation
window.addEventListener('load', function() {
  const header = document.querySelector('.main-header');
  if (header) {
    header.classList.add('loaded');
  }
});