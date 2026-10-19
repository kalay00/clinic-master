/**
 * 统一错误处理组件
 * 提供统一的错误提示和错误处理机制
 */

/**
 * 错误提示组件
 */
class ErrorHandler {
    /**
     * 显示错误提示
     * @param {string|Error} error - 错误信息或错误对象
     * @param {object} options - 配置选项
     */
    static showError(error, options = {}) {
        const {
            title = '错误',
            duration = 5000,
            position = 'top-end',
            showCloseButton = true,
            type = 'error'
        } = options;

        let message = '';
        if (typeof error === 'string') {
            message = error;
        } else if (error instanceof Error) {
            message = error.message;
        } else if (error && error.message) {
            message = error.message;
        } else {
            message = '发生未知错误';
        }

        // 使用Toast显示错误
        this.showToast(message, type, {
            title,
            duration,
            position,
            showCloseButton
        });
    }

    /**
     * 显示成功提示
     * @param {string} message - 成功消息
     * @param {object} options - 配置选项
     */
    static showSuccess(message, options = {}) {
        this.showToast(message, 'success', options);
    }

    /**
     * 显示警告提示
     * @param {string} message - 警告消息
     * @param {object} options - 配置选项
     */
    static showWarning(message, options = {}) {
        this.showToast(message, 'warning', options);
    }

    /**
     * 显示信息提示
     * @param {string} message - 信息消息
     * @param {object} options - 配置选项
     */
    static showInfo(message, options = {}) {
        this.showToast(message, 'info', options);
    }

    /**
     * 显示Toast通知
     * @param {string} message - 消息内容
     * @param {string} type - 类型 (success, error, warning, info)
     * @param {object} options - 配置选项
     */
    static showToast(message, type = 'info', options = {}) {
        const {
            title = null,
            duration = 5000,
            position = 'top-end',
            showCloseButton = true,
            icon = null
        } = options;

        // 获取图标
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };

        // 获取颜色
        const colors = {
            success: 'success',
            error: 'danger',
            warning: 'warning',
            info: 'info'
        };

        const toastIcon = icon || icons[type] || icons.info;
        const toastColor = colors[type] || colors.info;

        // 创建Toast容器（如果不存在）
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = `toast-container position-fixed ${this.getPositionClass(position)} p-3`;
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        // 创建Toast
        const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${toastColor} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        let toastHtml = '<div class="d-flex">';
        toastHtml += '<div class="toast-body">';
        if (title) {
            toastHtml += `<strong>${title}</strong><br>`;
        }
        if (toastIcon) {
            toastHtml += `<i class="bi ${toastIcon} me-2"></i>`;
        }
        toastHtml += message;
        toastHtml += '</div>';
        if (showCloseButton) {
            toastHtml += '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>';
        }
        toastHtml += '</div>';

        toast.innerHTML = toastHtml;
        toastContainer.appendChild(toast);

        // 初始化Bootstrap Toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: duration > 0,
            delay: duration
        });

        // Toast关闭后移除元素
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });

        // 显示Toast
        bsToast.show();
    }

    /**
     * 获取位置类
     * @param {string} position - 位置
     * @returns {string} CSS类
     */
    static getPositionClass(position) {
        const positions = {
            'top-start': 'top-0 start-0',
            'top-center': 'top-0 start-50 translate-middle-x',
            'top-end': 'top-0 end-0',
            'middle-start': 'top-50 start-0 translate-middle-y',
            'middle-center': 'top-50 start-50 translate-middle',
            'middle-end': 'top-50 end-0 translate-middle-y',
            'bottom-start': 'bottom-0 start-0',
            'bottom-center': 'bottom-0 start-50 translate-middle-x',
            'bottom-end': 'bottom-0 end-0'
        };
        return positions[position] || positions['top-end'];
    }

    /**
     * 处理API错误
     * @param {Error|object} error - 错误对象
     * @param {object} options - 配置选项
     */
    static handleApiError(error, options = {}) {
        const {
            showToast = true,
            defaultMessage = '操作失败，请稍后重试'
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
        } else if (code === 422) {
            // 422验证错误，显示详细错误信息
            if (error && error.response && error.response.data) {
                const errorData = error.response.data;
                if (errorData.data && errorData.data.details && errorData.data.details.errors) {
                    const validationErrors = errorData.data.details.errors;
                    const errorDetails = validationErrors.map(err => {
                        const field = err.loc ? err.loc.slice(1).join('.') : '未知字段';
                        const msg = err.msg || '验证失败';
                        return `${field}: ${msg}`;
                    }).join('\n');
                    message = `${message}\n\n${errorDetails}`;
                }
            }
        } else if (code === 500) {
            message = '服务器内部错误，请稍后重试';
        }

        if (showToast) {
            this.showError(message, {
                title: code ? `错误 (${code})` : '错误'
            });
        }

        return {
            message,
            code,
            error
        };
    }

    /**
     * 显示确认对话框（带错误提示）
     * @param {string} message - 确认消息
     * @param {object} options - 配置选项
     * @returns {Promise<boolean>} 用户确认结果
     */
    static async confirmWithError(message, options = {}) {
        const {
            title = '确认操作',
            confirmText = '确定',
            cancelText = '取消',
            type = 'warning'
        } = options;

        // 检查ModalComponents是否已加载
        if (typeof window.ModalComponents === 'undefined' || !window.ModalComponents) {
            // 如果未加载，使用原生confirm
            return window.confirm(message);
        }

        return await window.ModalComponents.confirm({
            title,
            message,
            confirmText,
            cancelText,
            confirmType: type === 'danger' ? 'danger' : 'primary'
        });
    }
}

// 全局错误处理
window.addEventListener('error', (event) => {
    console.error('全局错误:', event.error);
    ErrorHandler.showError(event.error.message || '发生未知错误', {
        title: '系统错误'
    });
});

// 未捕获的Promise错误
window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise错误:', event.reason);
    ErrorHandler.handleApiError(event.reason);
});

// 导出到全局
window.ErrorHandler = ErrorHandler;

// 如果存在增强版，优先使用增强版
if (window.ErrorHandlerEnhanced) {
    // 保持向后兼容，但使用增强版的功能
    Object.assign(ErrorHandler, ErrorHandlerEnhanced);
}

