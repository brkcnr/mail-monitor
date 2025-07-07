// Email Tracker JavaScript functionality with real-time updates

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

// Real-time functionality
function updateConnectionStatus(status) {
    const navIndicator = document.getElementById('nav-connection-indicator');
    const navText = document.getElementById('nav-connection-text');
    const statusBar = document.getElementById('status-bar');
    const statusIndicator = document.getElementById('status-indicator');
    const connectionStatus = document.getElementById('connection-status');
    
    if (navIndicator && navText) {
        switch(status) {
            case 'connected':
                navIndicator.className = 'w-2 h-2 bg-green-400 rounded-full animate-pulse';
                navText.textContent = 'Live';
                if (statusBar) statusBar.classList.remove('hidden');
                if (statusIndicator) statusIndicator.className = 'w-2 h-2 bg-white rounded-full animate-pulse';
                if (connectionStatus) connectionStatus.textContent = 'Connected';
                break;
            case 'disconnected':
                navIndicator.className = 'w-2 h-2 bg-red-400 rounded-full';
                navText.textContent = 'Offline';
                if (statusBar) statusBar.classList.add('hidden');
                break;
            case 'connecting':
                navIndicator.className = 'w-2 h-2 bg-yellow-400 rounded-full animate-bounce';
                navText.textContent = 'Connecting...';
                break;
        }
    }
}

function handleNewEmail(data) {
    // Update email count in real-time
    const totalEmailsElement = document.getElementById('total-emails');
    if (totalEmailsElement) {
        const currentCount = parseInt(totalEmailsElement.textContent) || 0;
        totalEmailsElement.textContent = currentCount + 1;
        totalEmailsElement.parentElement.style.transform = 'scale(1.05)';
        setTimeout(() => {
            totalEmailsElement.parentElement.style.transform = 'scale(1)';
        }, 300);
    }
    
    // Add new email to the list if on emails page
    const emailsTable = document.querySelector('#emails-table tbody');
    if (emailsTable) {
        const newRow = createEmailRow(data);
        emailsTable.insertBefore(newRow, emailsTable.firstChild);
        newRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Update recent emails on dashboard
    const recentEmailsList = document.querySelector('.recent-emails-list');
    if (recentEmailsList) {
        const newEmailElement = createRecentEmailElement(data);
        recentEmailsList.insertBefore(newEmailElement, recentEmailsList.firstChild);
        
        // Remove oldest if more than 5
        const recentEmails = recentEmailsList.querySelectorAll('.recent-email-item');
        if (recentEmails.length > 5) {
            recentEmails[recentEmails.length - 1].remove();
        }
    }
    
    // Show notification
    showNotification(`New email from ${data.sender}: ${data.subject.substring(0, 50)}...`, 'info');
    
    // Play notification sound (optional)
    playNotificationSound();
}

function createEmailRow(emailData) {
    const row = document.createElement('tr');
    row.className = 'email-row hover:bg-gray-50 transition-colors animate-fade-in';
    row.dataset.sender = emailData.sender.toLowerCase();
    row.dataset.subject = emailData.subject.toLowerCase();
    row.dataset.hasAttachment = emailData.has_attachment;
    
    const senderParts = emailData.sender.includes('@') ? emailData.sender.split('@') : [emailData.sender, ''];
    
    row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-user text-primary-600"></i>
                </div>
                <div class="min-w-0 flex-1">
                    <div class="text-sm font-medium text-gray-900 truncate">${senderParts[0]}</div>
                    <div class="text-sm text-gray-500 truncate">${senderParts[1]}</div>
                </div>
            </div>
        </td>
        <td class="px-6 py-4">
            <div class="text-sm text-gray-900 max-w-xs truncate">
                ${emailData.subject.length > 80 ? emailData.subject.substring(0, 80) + '...' : emailData.subject}
            </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm text-gray-500">${emailData.received_date}</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            ${emailData.has_attachment ? 
                `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <i class="fas fa-paperclip mr-1"></i>${emailData.attachment_count}
                </span>` : 
                '<span class="text-gray-400">—</span>'
            }
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <a href="/emails/${emailData.id}" 
               class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 transition-colors">
                <i class="fas fa-eye mr-1"></i>View
            </a>
        </td>
    `;
    
    return row;
}

function createRecentEmailElement(emailData) {
    const element = document.createElement('tr');
    element.className = 'recent-email-item hover:bg-gray-50 transition-colors animate-slide-in';
    
    element.innerHTML = `
        <td class="py-4 px-4">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-user text-primary-600 text-sm"></i>
                </div>
                <span class="text-sm text-gray-900 truncate max-w-xs">
                    ${emailData.sender.length > 50 ? emailData.sender.substring(0, 50) + '...' : emailData.sender}
                </span>
            </div>
        </td>
        <td class="py-4 px-4">
            <a href="/emails/${emailData.id}" 
               class="text-sm text-primary-600 hover:text-primary-800 hover:underline max-w-xs truncate block">
                ${emailData.subject.length > 60 ? emailData.subject.substring(0, 60) + '...' : emailData.subject}
            </a>
        </td>
        <td class="py-4 px-4">
            <span class="text-sm text-gray-500">${emailData.received_date}</span>
        </td>
        <td class="py-4 px-4">
            ${emailData.has_attachment ? 
                `<div class="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-paperclip text-green-600 text-xs"></i>
                </div>` : 
                `<div class="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-minus text-gray-400 text-xs"></i>
                </div>`
            }
        </td>
    `;
    
    return element;
}

function handleStatusUpdate(data) {
    const statusMessage = document.getElementById('status-message');
    const lastCheckTime = document.getElementById('last-check-time');
    const statusBar = document.getElementById('status-bar');
    
    if (statusMessage) {
        statusMessage.textContent = data.message;
    }
    
    if (lastCheckTime && data.last_check) {
        lastCheckTime.textContent = `Last check: ${data.last_check}`;
    }
    
    // Update status bar color based on status type
    if (statusBar) {
        statusBar.className = statusBar.className.replace(/from-\w+-\d+\s+to-\w+-\d+/, '');
        
        switch(data.type) {
            case 'error':
                statusBar.className += ' from-red-500 to-red-600';
                break;
            case 'checking':
                statusBar.className += ' from-blue-500 to-blue-600';
                break;
            case 'connection':
                statusBar.className += ' from-yellow-500 to-yellow-600';
                break;
            default:
                statusBar.className += ' from-green-500 to-green-600';
        }
    }
}

function playNotificationSound() {
    // Create a subtle notification sound
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
    oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
    
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
    gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.2);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.2);
}

// ... existing functions (viewAttachment, closeAttachmentModal, etc.) ...
// [Keep all the existing functions from the previous app.js file]

function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notifications-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `transform transition-all duration-300 translate-x-full opacity-0`;
    
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
    
    notification.innerHTML = `
        <div class="p-4 rounded-lg shadow-lg max-w-sm ${bgColors[type] || bgColors.info} text-white">
            <div class="flex items-start space-x-3">
                <i class="${icons[type] || icons.info} mt-0.5"></i>
                <div class="flex-1">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <button onclick="this.closest('[class*=translate]').remove()" 
                        class="text-white hover:text-gray-200 transition-colors">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Animate in
    requestAnimationFrame(() => {
        notification.classList.remove('translate-x-full', 'opacity-0');
    });
    
    // Auto remove
    setTimeout(() => {
        notification.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, duration);
}

// Update existing functions to support real-time features
function refreshStats() {
    // Stats are now updated via WebSocket, but keep this for manual refresh
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
        'last-updated': 'Updated ' + (data.last_updated || new Date().toLocaleTimeString())
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            // Add animation effect
            element.style.transform = 'scale(1.05)';
            element.style.transition = 'transform 0.2s ease';
            
            setTimeout(() => {
                element.textContent = value;
                element.style.transform = 'scale(1)';
            }, 100);
        }
    });
}

// Export functions for global use
window.EmailTracker = {
    refreshStats,
    updateStatsDisplay,
    showNotification,
    updateConnectionStatus,
    handleNewEmail,
    handleStatusUpdate,
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(function() {
            showNotification('Copied to clipboard!', 'success');
        }).catch(function() {
            showNotification('Failed to copy to clipboard', 'error');
        });
    },
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    },
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    // ... other existing functions
};

// Initialize real-time email list functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const filterSelect = document.getElementById('filter-attachments');
    
    if (searchInput) {
        searchInput.addEventListener('input', EmailTracker.debounce(filterEmails, 300));
    }
    
    if (filterSelect) {
        filterSelect.addEventListener('change', filterEmails);
    }
});

// Keep existing filter functions
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

// Add the missing functions from the original app.js
function viewAttachment(attachmentId, filename) {
    const modal = document.getElementById('attachment-modal');
    const modalTitle = document.getElementById('attachment-modal-title');
    const contentDiv = document.getElementById('attachment-content');
    
    modalTitle.textContent = filename;
    contentDiv.innerHTML = '<div class="text-center py-8"><i class="fas fa-spinner fa-spin text-2xl text-gray-500"></i><p class="mt-2 text-gray-500">Loading...</p></div>';
    
    modal.classList.remove('hidden');
    
    const fileExt = filename.split('.').pop().toLowerCase();
    const viewUrl = `/api/attachments/${attachmentId}/view`;
    
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(fileExt)) {
        contentDiv.innerHTML = `
            <div class="text-center">
                <img src="${viewUrl}" alt="${filename}" class="max-w-full max-h-96 mx-auto rounded-lg shadow-lg">
            </div>
        `;
    } else if (fileExt === 'pdf') {
        contentDiv.innerHTML = `
            <div class="w-full h-96">
                <iframe src="${viewUrl}" class="w-full h-full border rounded-lg" type="application/pdf">
                    <p>Your browser doesn't support PDF viewing. <a href="${viewUrl}" target="_blank" class="text-primary-600 hover:underline">Click here to view the PDF</a></p>
                </iframe>
            </div>
        `;
    } else if (fileExt === 'txt') {
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

// Update the global exports
Object.assign(window.EmailTracker, {
    viewAttachment,
    closeAttachmentModal,
    downloadAllAttachments,
    filterEmails,
    clearFilters
});