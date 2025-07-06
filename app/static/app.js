// Email Tracker JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('[data-auto-dismiss]');
        alerts.forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s ease-out';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);

    // Add loading states to form buttons
    document.querySelectorAll('button[type="submit"]').forEach(function(button) {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                this.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
                this.disabled = true;
            }
        });
    });

    // Initialize any tooltips or other components
    initializeComponents();
});

function initializeComponents() {
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Attachment viewer functionality
function viewAttachment(attachmentId, filename) {
    const modal = document.getElementById('attachment-modal');
    const modalTitle = document.getElementById('attachment-modal-title');
    const contentDiv = document.getElementById('attachment-content');
    
    modalTitle.textContent = filename;
    contentDiv.innerHTML = '<div class="text-center py-8"><i class="fas fa-spinner fa-spin text-2xl text-gray-500"></i><p class="mt-2 text-gray-500">Loading...</p></div>';
    
    modal.classList.remove('hidden');
    
    // Determine file type and load content
    const fileExt = filename.split('.').pop().toLowerCase();
    const viewUrl = `/api/attachments/${attachmentId}/view`;
    
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(fileExt)) {
        // Display image
        contentDiv.innerHTML = `
            <div class="text-center">
                <img src="${viewUrl}" alt="${filename}" class="max-w-full max-h-96 mx-auto rounded-lg shadow-lg">
            </div>
        `;
    } else if (fileExt === 'pdf') {
        // Display PDF
        contentDiv.innerHTML = `
            <div class="w-full h-96">
                <iframe src="${viewUrl}" class="w-full h-full border rounded-lg" type="application/pdf">
                    <p>Your browser doesn't support PDF viewing. <a href="${viewUrl}" target="_blank" class="text-primary-600 hover:underline">Click here to view the PDF</a></p>
                </iframe>
            </div>
        `;
    } else if (fileExt === 'txt') {
        // Display text content
        fetch(viewUrl)
            .then(response => response.text())
            .then(text => {
                contentDiv.innerHTML = `
                    <div class="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                        <pre class="whitespace-pre-wrap text-sm text-gray-700">${text}</pre>
                    </div>
                `;
            })
            .catch(error => {
                contentDiv.innerHTML = `
                    <div class="text-center py-8 text-red-500">
                        <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                        <p>Error loading file content</p>
                    </div>
                `;
            });
    } else {
        contentDiv.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-file text-6xl mb-4"></i>
                <p class="mb-4">This file type cannot be previewed.</p>
                <a href="/api/attachments/${attachmentId}/download" 
                   class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700">
                    <i class="fas fa-download mr-2"></i>Download to view
                </a>
            </div>
        `;
    }
}

function closeAttachmentModal() {
    const modal = document.getElementById('attachment-modal');
    modal.classList.add('hidden');
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('attachment-modal');
    if (event.target === modal) {
        closeAttachmentModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeAttachmentModal();
    }
});

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Copied to clipboard!', 'success');
    }).catch(function() {
        showNotification('Failed to copy to clipboard', 'error');
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transform transition-all duration-300 translate-x-full`;
    
    const bgColors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-triangle',
        warning: 'fas fa-exclamation-circle',
        info: 'fas fa-info-circle'
    };
    
    notification.className += ` ${bgColors[type] || bgColors.info} text-white`;
    notification.innerHTML = `
        <div class="flex items-center space-x-2">
            <i class="${icons[type] || icons.info}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Stats refresh functionality
function refreshStats() {
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                updateStatsDisplay(data);
            }
        })
        .catch(error => {
            console.error('Error refreshing stats:', error);
            showNotification('Failed to refresh stats', 'error');
        });
}

function updateStatsDisplay(data) {
    const elements = {
        'total-emails': data.total_emails,
        'emails-with-attachments': data.emails_with_attachments,
        'monitoring-status': data.monitoring_status,
        'last-updated': 'Updated ' + new Date().toLocaleTimeString()
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            element.style.transform = 'scale(1.05)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
    });
}

// Email detail page functionality
function downloadAllAttachments() {
    const attachmentUrlsElement = document.getElementById('attachment-urls');
    if (attachmentUrlsElement) {
        try {
            const attachmentUrls = JSON.parse(attachmentUrlsElement.textContent);
            
            if (attachmentUrls.length === 0) {
                showNotification('No attachments to download', 'warning');
                return;
            }
            
            showNotification(`Starting download of ${attachmentUrls.length} attachment(s)...`, 'info');
            
            attachmentUrls.forEach((url, index) => {
                setTimeout(() => {
                    const link = document.createElement('a');
                    link.href = url;
                    link.target = '_blank';
                    link.style.display = 'none';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }, index * 500);
            });
            
        } catch (error) {
            console.error('Error parsing attachment URLs:', error);
            showNotification('Error downloading attachments', 'error');
        }
    } else {
        showNotification('No attachments found', 'warning');
    }
}

// Search and filter functionality
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function filterEmails() {
    const searchInput = document.getElementById('search-input');
    const filterSelect = document.getElementById('filter-attachments');
    
    if (!searchInput || !filterSelect) return;
    
    const searchTerm = searchInput.value.toLowerCase();
    const attachmentFilter = filterSelect.value;
    const rows = document.querySelectorAll('.email-row');

    let visibleCount = 0;
    
    rows.forEach(row => {
        const sender = row.dataset.sender || '';
        const subject = row.dataset.subject || '';
        const hasAttachment = row.dataset.hasAttachment === 'True';
        
        const matchesSearch = sender.includes(searchTerm) || subject.includes(searchTerm);
        
        let matchesFilter = true;
        if (attachmentFilter === 'with') {
            matchesFilter = hasAttachment;
        } else if (attachmentFilter === 'without') {
            matchesFilter = !hasAttachment;
        }
        
        const shouldShow = matchesSearch && matchesFilter;
        row.style.display = shouldShow ? '' : 'none';
        
        if (shouldShow) visibleCount++;
    });
    
    const resultsCount = document.getElementById('results-count');
    if (resultsCount) {
        resultsCount.textContent = `${visibleCount} email(s) found`;
    }
}

function clearFilters() {
    const searchInput = document.getElementById('search-input');
    const filterSelect = document.getElementById('filter-attachments');
    
    if (searchInput) searchInput.value = '';
    if (filterSelect) filterSelect.value = '';
    
    filterEmails();
    showNotification('Filters cleared', 'success');
}

// Initialize email list functionality when page loads
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const filterSelect = document.getElementById('filter-attachments');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterEmails, 300));
    }
    
    if (filterSelect) {
        filterSelect.addEventListener('change', filterEmails);
    }
});

// Export functions for global use
window.EmailTracker = {
    refreshStats,
    updateStatsDisplay,
    showNotification,
    copyToClipboard,
    formatDate,
    debounce,
    downloadAllAttachments,
    filterEmails,
    clearFilters,
    viewAttachment,
    closeAttachmentModal
};