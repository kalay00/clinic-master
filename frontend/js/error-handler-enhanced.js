/**
 * 增强版统一错误处理组件
 * 提供统一的错误提示和错误处理机制，支持更多自定义选项和更好的用户体验
 */

/**
 * 错误提示组件（增强版）
 */
class ErrorHandlerEnhanced {
    static instance = null;
    toastQueue = [];
    maxToasts = 5;
    isProcessingQueue = false;

    constructor() {
        if (ErrorHandlerEnhanced.instance) {
            return ErrorHandlerEnhanced.instance;
        }
        ErrorHandlerEnhanced.instance = this;
        this.init();
    }

    /**
     * 初始化
     */
    init() {
        // 创建Toast容器
        this.createToastContainer();
        // 处理队列
        this.processQueue();
    }

    /**
     * 创建Toast容器
     */
    createToastContainer() {
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            container.style.maxWidth = '400px';
            document.body.appendChild(container);
        }
    }

    /**
     * 显示错误提示（增强版）
     * @param {string|Error} error - 错误信息或错误对象
     * @param {object} options - 配置选项
     */
    static showError(error, options = {}) {
        const instance = ErrorHandlerEnhanced.getInstance();
        return instance._showMessage(error, 'error', {
            title: '错误',
            icon: 'bi-x-circle-fill',
            color: 'danger',
            ...options
        });
    }

    /**
     * 显示成功提示（增强版）
     * @param {string} message - 成功消息
     * @param {object} options - 配置选项
     */
    static showSuccess(message, options = {}) {
        const instance = ErrorHandlerEnhanced.getInstance();
        return instance._showMessage(message, 'success', {
            title: '成功',
            icon: 'bi-check-circle-fill',
            color: 'success',
            duration: 3000,
            ...options
        });
    }

    /**
     * 显示警告提示（增强版）
     * @param {string} message - 警告消息
     * @param {object} options - 配置选项
     */
    static showWarning(message, options = {}) {
        const instance = ErrorHandlerEnhanced.getInstance();
        return instance._showMessage(message, 'warning', {
            title: '警告',
            icon: 'bi-exclamation-triangle-fill',
            color: 'warning',
            duration: 4000,
            ...options
        });
    }

    /**
     * 显示信息提示（增强版）
     * @param {string} message - 信息消息
     * @param {object} options - 配置选项
     */
    static showInfo(message, options = {}) {
        const instance = ErrorHandlerEnhanced.getInstance();
        return instance._showMessage(message, 'info', {
            title: '提示',
            icon: 'bi-info-circle-fill',
            color: 'info',
            duration: 3000,
            ...options
        });
    }

    /**
     * 显示消息（内部方法）
     * @param {string|Error} message - 消息内容
     * @param {string} type - 类型
     * @param {object} options - 配置选项
     */
    _showMessage(message, type, options = {}) {
        const {
            title = null,
            duration = 5000,
            position = 'top-end',
            showCloseButton = true,
            icon = null,
            color = 'info',
            showProgress = true,
            action = null,
            actionText = null,
            persistent = false,
            group = null,
            merge = false
        } = options;

        // 解析消息
        let messageText = '';
        if (typeof message === 'string') {
            messageText = message;
        } else if (message instanceof Error) {
            messageText = message.message;
        } else if (message && message.message) {
            messageText = message.message;
        } else {
            messageText = '发生未知错误';
        }

        // 如果启用合并，检查是否有相同类型的消息
        if (merge && group) {
            const existingToast = this.findToastByGroup(group);
            if (existingToast) {
                this.updateToast(existingToast, messageText, options);
                return existingToast.id;
            }
        }

        // 添加到队列
        const toastData = {
            id: `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            message: messageText,
            type,
            title,
            duration,
            position,
            showCloseButton,
            icon: icon || options.icon,
            color,
            showProgress,
            action,
            actionText,
            persistent: persistent || duration === 0,
            group,
            timestamp: Date.now()
        };

        this.toastQueue.push(toastData);
        this.processQueue();

        return toastData.id;
    }

    /**
     * 查找相同组的Toast
     */
    findToastByGroup(group) {
        const container = document.getElementById('toast-container');
        if (!container) return null;

        const toasts = container.querySelectorAll(`[data-group="${group}"]`);
        if (toasts.length > 0) {
            return {
                id: toasts[0].id,
                element: toasts[0]
            };
        }
        return null;
    }

    /**
     * 更新Toast内容
     */
    updateToast(toastInfo, newMessage, options) {
        const toastElement = document.getElementById(toastInfo.id);
        if (!toastElement) return;

        const body = toastElement.querySelector('.toast-body');
        if (body) {
            const count = parseInt(toastElement.dataset.count || '1') + 1;
            toastElement.dataset.count = count;
            body.innerHTML = `
                ${options.title ? `<strong>${options.title}</strong><br>` : ''}
                ${options.icon ? `<i class="bi ${options.icon} me-2"></i>` : ''}
                ${newMessage}
                <span class="badge bg-light text-dark ms-2">${count}</span>
            `;
        }
    }

    /**
     * 处理Toast队列
     */
    async processQueue() {
        if (this.isProcessingQueue || this.toastQueue.length === 0) {
            return;
        }

        this.isProcessingQueue = true;

        while (this.toastQueue.length > 0) {
            // 检查当前Toast数量
            const currentToasts = document.querySelectorAll('.toast.show, .toast:not(.hide)');
            if (currentToasts.length >= this.maxToasts) {
                // 等待一段时间后重试
                await this.sleep(500);
                continue;
            }

            const toastData = this.toastQueue.shift();
            this.createToast(toastData);
            
            // 短暂延迟，避免同时显示太多
            if (this.toastQueue.length > 0) {
                await this.sleep(100);
            }
        }

        this.isProcessingQueue = false;
    }

    /**
     * 创建Toast元素
     */
    createToast(toastData) {
        const container = document.getElementById('toast-container');
        if (!container) {
            this.createToastContainer();
            return this.createToast(toastData);
        }

        const toast = document.createElement('div');
        toast.id = toastData.id;
        toast.className = `toast align-items-center text-white bg-${toastData.color} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        if (toastData.group) {
            toast.setAttribute('data-group', toastData.group);
        }

        // 构建Toast内容
        let toastHtml = '<div class="d-flex">';
        
        // 进度条
        if (toastData.showProgress && toastData.duration > 0) {
            toastHtml += `<div class="toast-progress" style="position: absolute; bottom: 0; left: 0; height: 3px; background: rgba(255,255,255,0.3); width: 100%;">
                <div class="toast-progress-bar" style="height: 100%; background: rgba(255,255,255,0.8); width: 100%; transition: width ${toastData.duration}ms linear;"></div>
            </div>`;
        }

        toastHtml += '<div class="toast-body">';
        if (toastData.title) {
            toastHtml += `<strong>${toastData.title}</strong><br>`;
        }
        if (toastData.icon) {
            toastHtml += `<i class="bi ${toastData.icon} me-2"></i>`;
        }
        toastHtml += toastData.message;
        
        // 操作按钮
        if (toastData.action && toastData.actionText) {
            toastHtml += `<div class="mt-2">
                <button type="button" class="btn btn-sm btn-light" data-action="custom">${toastData.actionText}</button>
            </div>`;
        }
        
        toastHtml += '</div>';
        
        if (toastData.showCloseButton) {
            toastHtml += '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>';
        }
        toastHtml += '</div>';

        toast.innerHTML = toastHtml;
        container.appendChild(toast);

        // 初始化Bootstrap Toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: !toastData.persistent && toastData.duration > 0,
            delay: toastData.duration
        });

        // 进度条动画
        if (toastData.showProgress && toastData.duration > 0) {
            const progressBar = toast.querySelector('.toast-progress-bar');
            if (progressBar) {
                setTimeout(() => {
                    progressBar.style.width = '0%';
                }, 50);
            }
        }

        // 自定义操作
        if (toastData.action) {
            const actionBtn = toast.querySelector('[data-action="custom"]');
            if (actionBtn) {
                actionBtn.addEventListener('click', () => {
                    toastData.action();
                    bsToast.hide();
                });
            }
        }

        // Toast关闭后移除
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
            // 继续处理队列
            this.processQueue();
        });

        // 显示Toast
        bsToast.show();

        return toastData.id;
    }

    /**
     * 处理API错误（增强版）
     * @param {Error|object} error - 错误对象
     * @param {object} options - 配置选项
     */
    static handleApiError(error, options = {}) {
        const instance = ErrorHandlerEnhanced.getInstance();
        return instance._handleApiError(error, options);
    }

    /**
     * 处理API错误（内部方法）
     */
    _handleApiError(error, options = {}) {
        const {
            showToast = true,
            defaultMessage = '操作失败，请稍后重试',
            group = 'api-errors',
            merge = true,
            retry = null,
            retryText = '重试'
        } = options;

        let message = defaultMessage;
        let code = null;

        // 解析错误信息
        if (error && error.message) {
            message = error.message;
        } else if (typeof error === 'string') {
            message = error;
        }

        // 如果是API响应错误
        if (error && error.response) {
            try {
                const errorData = error.response.data || error.response;
                if (errorData.message) {
                    message = errorData.message;
                }
                if (errorData.code) {
                    code = errorData.code;
                }
            } catch (e) {
                // 忽略解析错误
            }
        }

        // 根据错误代码显示不同的提示
        if (code === 401) {
            message = '登录已过期，请重新登录';
        } else if (code === 403) {
            message = '没有权限执行此操作';
        } else if (code === 404) {
            message = '资源不存在';
        } else if (code === 500) {
            message = '服务器内部错误，请稍后重试';
        }

        if (showToast) {
            const toastOptions = {
                title: code ? `错误 (${code})` : '错误',
                group,
                merge,
                action: retry,
                actionText: retry ? retryText : null,
                persistent: !!retry
            };
            this._showMessage(message, 'error', toastOptions);
        }

        return {
            message,
            code,
            error
        };
    }

    /**
     * 显示确认对话框（增强版）
     * @param {string} message - 确认消息
     * @param {object} options - 配置选项
     * @returns {Promise<boolean>} 用户确认结果
     */
    static async confirmWithError(message, options = {}) {
        const {
            title = '确认操作',
            confirmText = '确定',
            cancelText = '取消',
            type = 'warning',
            icon = null,
            persistent = false
        } = options;

        return await ModalComponents.confirm({
            title,
            message,
            confirmText,
            cancelText,
            confirmType: type === 'danger' ? 'danger' : 'primary',
            icon,
            persistent
        });
    }

    /**
     * 清除所有Toast
     */
    static clearAll() {
        const container = document.getElementById('toast-container');
        if (container) {
            container.querySelectorAll('.toast').forEach(toast => {
                const bsToast = bootstrap.Toast.getInstance(toast);
                if (bsToast) {
                    bsToast.hide();
                } else {
                    toast.remove();
                }
            });
        }
    }

    /**
     * 清除指定类型的Toast
     * @param {string} type - Toast类型
     */
    static clearByType(type) {
        const container = document.getElementById('toast-container');
        if (container) {
            container.querySelectorAll(`.toast.bg-${type}`).forEach(toast => {
                const bsToast = bootstrap.Toast.getInstance(toast);
                if (bsToast) {
                    bsToast.hide();
                } else {
                    toast.remove();
                }
            });
        }
    }

    /**
     * 获取实例
     */
    static getInstance() {
        if (!ErrorHandlerEnhanced.instance) {
            ErrorHandlerEnhanced.instance = new ErrorHandlerEnhanced();
        }
        return ErrorHandlerEnhanced.instance;
    }

    /**
     * 睡眠函数
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// 全局错误处理
window.addEventListener('error', (event) => {
    console.error('全局错误:', event.error);
    ErrorHandlerEnhanced.showError(event.error.message || '发生未知错误', {
        title: '系统错误',
        persistent: false
    });
});

// 未捕获的Promise错误
window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise错误:', event.reason);
    ErrorHandlerEnhanced.handleApiError(event.reason);
});

// 导出到全局（兼容旧版本）
window.ErrorHandlerEnhanced = ErrorHandlerEnhanced;
// 如果旧版本ErrorHandler不存在，使用增强版
if (!window.ErrorHandler) {
    window.ErrorHandler = ErrorHandlerEnhanced;
}

