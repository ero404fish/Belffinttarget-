/* 
 * Belffin Target运营工具 - 主脚本文件
 * 创建日期: 2025-03-21
 */

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化表单验证
    initFormValidation();
    
    // 添加响应式表格支持
    initResponsiveTables();
    
    // 添加动画效果
    addAnimationEffects();
    
    // 初始化导航高亮
    highlightCurrentNav();
});

// 初始化工具提示
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 初始化表单验证
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// 初始化响应式表格
function initResponsiveTables() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.classList.add('table-responsive');
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// 添加动画效果
function addAnimationEffects() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.classList.add('fade-in');
    });
}

// 高亮当前导航项
function highlightCurrentNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });
}

// 通用确认对话框
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 显示加载指示器
function showLoading() {
    const loadingEl = document.createElement('div');
    loadingEl.classList.add('loading-overlay');
    loadingEl.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">加载中...</span></div>';
    document.body.appendChild(loadingEl);
}

// 隐藏加载指示器
function hideLoading() {
    const loadingEl = document.querySelector('.loading-overlay');
    if (loadingEl) {
        loadingEl.remove();
    }
}

// AJAX表单提交
function submitFormAjax(formId, successCallback, errorCallback) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const url = form.getAttribute('action');
        const method = form.getAttribute('method') || 'POST';
        
        showLoading();
        
        fetch(url, {
            method: method,
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (successCallback) successCallback(data);
        })
        .catch(error => {
            hideLoading();
            if (errorCallback) errorCallback(error);
            else console.error('Error:', error);
        });
    });
}
