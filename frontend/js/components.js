/**
 * 公共组件库
 * 提供可复用的UI组件
 */

/**
 * 表单组件
 */
const FormComponents = {
    /**
     * 创建表单输入框
     * @param {object} options - 配置选项
     * @returns {string} HTML字符串
     */
    createInput(options = {}) {
        const {
            id,
            label,
            type = 'text',
            name,
            value = '',
            placeholder = '',
            required = false,
            disabled = false,
            readonly = false,
            helpText = '',
            error = '',
            classes = '',
            min = null,
            max = null,
            step = null
        } = options;

        let html = '<div class="mb-3">';
        
        if (label) {
            html += `<label for="${id}" class="form-label">${label}${required ? ' <span class="text-danger">*</span>' : ''}</label>`;
        }
        
        const inputClasses = `form-control ${error ? 'is-invalid' : ''} ${classes}`;
        
        // 构建额外的属性字符串
        let extraAttrs = '';
        if (min !== null && min !== undefined) {
            extraAttrs += ` min="${min}"`;
        }
        if (max !== null && max !== undefined) {
            extraAttrs += ` max="${max}"`;
        }
        if (step !== null && step !== undefined) {
            extraAttrs += ` step="${step}"`;
        }
        
        html += `<input type="${type}" class="${inputClasses}" id="${id}" name="${name || id}" 
                value="${value}" placeholder="${placeholder}" 
                ${required ? 'required' : ''} ${disabled ? 'disabled' : ''} ${readonly ? 'readonly' : ''}${extraAttrs}>`;
        
        if (error) {
            html += `<div class="invalid-feedback">${error}</div>`;
        }
        
        if (helpText) {
            html += `<div class="form-text">${helpText}</div>`;
        }
        
        html += '</div>';
        return html;
    },

    /**
     * 创建下拉选择框
     * @param {object} options - 配置选项
     * @returns {string} HTML字符串
     */
    createSelect(options = {}) {
        const {
            id,
            label,
            name,
            options: selectOptions = [],
            value = '',
            required = false,
            disabled = false,
            placeholder = '请选择',
            error = '',
            classes = '',
            onChange = null
        } = options;

        let html = '<div class="mb-3">';
        
        if (label) {
            html += `<label for="${id}" class="form-label">${label}${required ? ' <span class="text-danger">*</span>' : ''}</label>`;
        }
        
        const selectClasses = `form-select ${error ? 'is-invalid' : ''} ${classes}`;
        const onChangeAttr = onChange ? `onchange="${onChange}"` : '';
        html += `<select class="${selectClasses}" id="${id}" name="${name || id}" 
                ${required ? 'required' : ''} ${disabled ? 'disabled' : ''} ${onChangeAttr}>`;
        
        if (placeholder) {
            html += `<option value="">${placeholder}</option>`;
        }
        
        selectOptions.forEach(option => {
            const isSelected = option.value === value || option.selected;
            html += `<option value="${option.value}" ${isSelected ? 'selected' : ''}>${option.text}</option>`;
        });
        
        html += '</select>';
        
        if (error) {
            html += `<div class="invalid-feedback">${error}</div>`;
        }
        
        html += '</div>';
        return html;
    },

    /**
     * 创建文本域
     * @param {object} options - 配置选项
     * @returns {string} HTML字符串
     */
    createTextarea(options = {}) {
        const {
            id,
            label,
            name,
            value = '',
            placeholder = '',
            rows = 3,
            required = false,
            disabled = false,
            error = '',
            classes = ''
        } = options;

        let html = '<div class="mb-3">';
        
        if (label) {
            html += `<label for="${id}" class="form-label">${label}${required ? ' <span class="text-danger">*</span>' : ''}</label>`;
        }
        
        const textareaClasses = `form-control ${error ? 'is-invalid' : ''} ${classes}`;
        html += `<textarea class="${textareaClasses}" id="${id}" name="${name || id}" 
                rows="${rows}" placeholder="${placeholder}" 
                ${required ? 'required' : ''} ${disabled ? 'disabled' : ''}>${value}</textarea>`;
        
        if (error) {
            html += `<div class="invalid-feedback">${error}</div>`;
        }
        
        html += '</div>';
        return html;
    },

    /**
     * 创建日期选择器
     * @param {object} options - 配置选项
     * @returns {string} HTML字符串
     */
    createDatePicker(options = {}) {
        const {
            id,
            label,
            name,
            value = '',
            required = false,
            disabled = false,
            error = '',
            classes = ''
        } = options;

        let html = '<div class="mb-3">';
        
        if (label) {
            html += `<label for="${id}" class="form-label">${label}${required ? ' <span class="text-danger">*</span>' : ''}</label>`;
        }
        
        const inputClasses = `form-control datepicker ${error ? 'is-invalid' : ''} ${classes}`;
        html += `<input type="date" class="${inputClasses}" id="${id}" name="${name || id}" 
                value="${value}" ${required ? 'required' : ''} ${disabled ? 'disabled' : ''}>`;
        
        if (error) {
            html += `<div class="invalid-feedback">${error}</div>`;
        }
        
        html += '</div>';
        return html;
    },

    /**
     * 创建复选框
     * @param {object} options - 配置选项
     * @returns {string} HTML字符串
     */
    createCheckbox(options = {}) {
        const {
            id,
            label,
            name,
            checked = false,
            disabled = false,
            value = '1',
            classes = ''
        } = options;

        let html = '<div class="form-check mb-3">';
        html += `<input class="form-check-input ${classes}" type="checkbox" id="${id}" 
                name="${name || id}" value="${value}" ${checked ? 'checked' : ''} ${disabled ? 'disabled' : ''}>`;
        html += `<label class="form-check-label" for="${id}">${label}</label>`;
        html += '</div>';
        return html;
    },

    /**
     * 创建单选框
     * @param {object} options - 配置选项
     * @returns {string} HTML字符串
     */
    createRadio(options = {}) {
        const {
            id,
            label,
            name,
            value,
            checked = false,
            disabled = false,
            classes = ''
        } = options;

        let html = '<div class="form-check mb-3">';
        html += `<input class="form-check-input ${classes}" type="radio" id="${id}" 
                name="${name}" value="${value}" ${checked ? 'checked' : ''} ${disabled ? 'disabled' : ''}>`;
        html += `<label class="form-check-label" for="${id}">${label}</label>`;
        html += '</div>';
        return html;
    }
};

/**
 * 表格组件
 */
const TableComponents = {
    /**
     * 渲染数据表格
     * @param {object} options - 配置选项
     * @returns {string} HTML字符串
     */
    renderTable(options = {}) {
        const {
            id = 'dataTable',
            columns = [],
            data = [],
            emptyText = '暂无数据',
            classes = '',
            striped = true,
            hover = true,
            bordered = false,
            responsive = true
        } = options;

        let html = '';
        
        if (responsive) {
            html += '<div class="table-responsive">';
        }
        
        const tableClasses = `table ${striped ? 'table-striped' : ''} ${hover ? 'table-hover' : ''} ${bordered ? 'table-bordered' : ''} ${classes}`;
        html += `<table class="${tableClasses}" id="${id}">`;
        
        // 表头
        if (columns.length > 0) {
            html += '<thead><tr>';
            columns.forEach(col => {
                const align = col.align || 'left';
                html += `<th style="text-align: ${align}">${col.title}</th>`;
            });
            html += '</tr></thead>';
        }
        
        // 表体
        html += '<tbody>';
        if (data.length === 0) {
            html += `<tr><td colspan="${columns.length}" class="text-center text-muted">${emptyText}</td></tr>`;
        } else {
            data.forEach((row, index) => {
                html += '<tr>';
                columns.forEach(col => {
                    const align = col.align || 'left';
                    const value = col.render ? col.render(row, index) : (row[col.key] || '');
                    html += `<td style="text-align: ${align}">${value}</td>`;
                });
                html += '</tr>';
            });
        }
        html += '</tbody>';
        
        html += '</table>';
        
        if (responsive) {
            html += '</div>';
        }
        
        return html;
    },

    /**
     * 渲染分页组件
     * @param {object} options - 配置选项
     * @returns {string} HTML字符串
     */
    renderPagination(options = {}) {
        const {
            currentPage = 1,
            totalPages = 1,
            totalItems = 0,
            pageSize = 10,
            onPageChange = null,
            showInfo = true
        } = options;

        // 生成唯一ID用于事件绑定
        const paginationId = `pagination-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        let html = `<nav aria-label="分页导航" id="${paginationId}">`;
        html += '<ul class="pagination justify-content-center">';
        
        // 上一页
        html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">`;
        html += `<a class="page-link" href="#" data-page="${currentPage - 1}" ${currentPage === 1 ? 'tabindex="-1" aria-disabled="true"' : ''}>上一页</a>`;
        html += '</li>';
        
        // 页码
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        if (startPage > 1) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
            if (startPage > 2) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === currentPage ? 'active' : ''}">`;
            html += `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
            html += '</li>';
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }
        
        // 下一页
        html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">`;
        html += `<a class="page-link" href="#" data-page="${currentPage + 1}" ${currentPage === totalPages ? 'tabindex="-1" aria-disabled="true"' : ''}>下一页</a>`;
        html += '</li>';
        
        html += '</ul>';
        html += '</nav>';
        
        if (showInfo) {
            const start = (currentPage - 1) * pageSize + 1;
            const end = Math.min(currentPage * pageSize, totalItems);
            html += `<div class="text-center text-muted mt-2">显示 ${start}-${end} 条，共 ${totalItems} 条</div>`;
        }
        
        // 绑定分页点击事件
        if (onPageChange) {
            setTimeout(() => {
                const paginationElement = document.getElementById(paginationId);
                if (paginationElement) {
                    paginationElement.querySelectorAll('.page-link').forEach(link => {
                        link.addEventListener('click', (e) => {
                            e.preventDefault();
                            const page = parseInt(link.dataset.page);
                            if (page && page !== currentPage && page >= 1 && page <= totalPages) {
                                onPageChange(page);
                            }
                        });
                    });
                }
            }, 100);
        }
        
        return html;
    }
};

/**
 * 弹窗组件
 */
const ModalComponents = {
    /**
     * 显示确认对话框
     * @param {object} options - 配置选项
     * @returns {Promise} 用户确认结果
     */
    async confirm(options = {}) {
        const {
            title = '确认',
            message = '确定要执行此操作吗？',
            confirmText = '确定',
            cancelText = '取消',
            confirmType = 'primary'
        } = options;

        return new Promise((resolve) => {
            const modalId = `confirm-modal-${Date.now()}`;
            const modalHtml = `
                <div class="modal fade" id="${modalId}" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>${message}</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${cancelText}</button>
                                <button type="button" class="btn btn-${confirmType}" id="confirm-btn">${confirmText}</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // 添加到页面
            const modalContainer = document.getElementById('modal-container') || (() => {
                const container = document.createElement('div');
                container.id = 'modal-container';
                document.body.appendChild(container);
                return container;
            })();
            
            modalContainer.insertAdjacentHTML('beforeend', modalHtml);
            
            const modalElement = document.getElementById(modalId);
            const modal = new bootstrap.Modal(modalElement, {
                focus: true,
                keyboard: true
            });
            
            // 等待模态框完全显示后再处理焦点（避免aria-hidden警告）
            modalElement.addEventListener('shown.bs.modal', () => {
                // 模态框完全显示后，确保焦点在模态框内
                const firstInput = modalElement.querySelector('input, textarea, select, button:not([data-bs-dismiss])');
                if (firstInput) {
                    firstInput.focus();
                }
            });
            
            // 确认按钮
            document.getElementById('confirm-btn').addEventListener('click', () => {
                modal.hide();
                resolve(true);
                modalElement.remove();
            });
            
            // 取消或关闭
            modalElement.addEventListener('hidden.bs.modal', () => {
                resolve(false);
                modalElement.remove();
            });
            
            modal.show();
        });
    },

    /**
     * 显示表单对话框
     * @param {object} options - 配置选项
     * @returns {Promise} 表单数据或null
     */
    async showFormModal(options = {}) {
        const {
            title = '表单',
            formHtml = '',
            onSubmit = null,
            onShow = null,
            size = ''
        } = options;

        return new Promise((resolve) => {
            const modalId = `form-modal-${Date.now()}`;
            const sizeClass = size ? `modal-${size}` : '';
            const modalHtml = `
                <div class="modal fade" id="${modalId}" tabindex="-1">
                    <div class="modal-dialog ${sizeClass}">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <form id="form-modal-form">
                                <div class="modal-body">
                                    ${formHtml}
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                    <button type="submit" class="btn btn-primary">确定</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            `;

            const modalContainer = document.getElementById('modal-container') || (() => {
                const container = document.createElement('div');
                container.id = 'modal-container';
                document.body.appendChild(container);
                return container;
            })();
            
            modalContainer.insertAdjacentHTML('beforeend', modalHtml);
            
            const modalElement = document.getElementById(modalId);
            const modal = new bootstrap.Modal(modalElement, {
                focus: true,
                keyboard: true
            });
            
            // 等待模态框完全显示后再处理焦点（避免aria-hidden警告）
            modalElement.addEventListener('shown.bs.modal', () => {
                // 模态框完全显示后，确保焦点在模态框内
                const firstInput = modalElement.querySelector('input, textarea, select, button:not([data-bs-dismiss])');
                if (firstInput) {
                    firstInput.focus();
                }
                
                // 调用onShow回调（如果提供）
                if (onShow && typeof onShow === 'function') {
                    try {
                        onShow(modalElement);
                    } catch (error) {
                        console.error('onShow回调执行失败:', error);
                    }
                }
            });
            
            // 表单提交
            document.getElementById('form-modal-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                if (onSubmit) {
                    const formData = new FormData(e.target);
                    const data = Object.fromEntries(formData);
                    const result = await onSubmit(data);
                    if (result !== false) {
                        modal.hide();
                        resolve(data);
                        modalElement.remove();
                    }
                } else {
                    const formData = new FormData(e.target);
                    const data = Object.fromEntries(formData);
                    modal.hide();
                    resolve(data);
                    modalElement.remove();
                }
            });
            
            // 关闭
            modalElement.addEventListener('hidden.bs.modal', () => {
                resolve(null);
                modalElement.remove();
            });
            
            modal.show();
        });
    },
    
    /**
     * 显示信息对话框
     * @param {object} options - 配置选项
     * @returns {Promise} 关闭时resolve
     */
    async showInfoModal(options = {}) {
        const {
            title = '信息',
            content = '',
            size = ''
        } = options;

        return new Promise((resolve) => {
            const modalId = `info-modal-${Date.now()}`;
            const sizeClass = size ? `modal-${size}` : '';
            const modalHtml = `
                <div class="modal fade" id="${modalId}" tabindex="-1">
                    <div class="modal-dialog ${sizeClass}">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                ${content}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-primary" data-bs-dismiss="modal">关闭</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            const modalContainer = document.getElementById('modal-container') || (() => {
                const container = document.createElement('div');
                container.id = 'modal-container';
                document.body.appendChild(container);
                return container;
            })();
            
            modalContainer.insertAdjacentHTML('beforeend', modalHtml);
            
            const modalElement = document.getElementById(modalId);
            const modal = new bootstrap.Modal(modalElement, {
                focus: true,
                keyboard: true
            });
            
            // 等待模态框完全显示后再处理焦点（避免aria-hidden警告）
            modalElement.addEventListener('shown.bs.modal', () => {
                // 模态框完全显示后，确保焦点在模态框内
                const firstInput = modalElement.querySelector('input, textarea, select, button:not([data-bs-dismiss])');
                if (firstInput) {
                    firstInput.focus();
                }
            });
            
            // 关闭
            modalElement.addEventListener('hidden.bs.modal', () => {
                resolve();
                modalElement.remove();
            });
            
            modal.show();
        });
    }
};

/**
 * 加载组件
 */
const LoadingComponents = {
    /**
     * 显示加载动画
     * @param {string} message - 加载提示
     * @param {string} target - 目标元素ID或选择器
     */
    show(message = '加载中...', target = 'main-content') {
        const targetElement = typeof target === 'string' ? document.getElementById(target) : target;
        if (!targetElement) return;

        const loadingId = `loading-${Date.now()}`;
        const loadingHtml = `
            <div id="${loadingId}" class="loading-overlay">
                <div class="loading-content">
                    <div class="loading-spinner" style="width: 50px; height: 50px; margin: 0 auto;"></div>
                    <p class="mt-3 text-center">${message}</p>
                </div>
            </div>
        `;

        targetElement.insertAdjacentHTML('beforeend', loadingHtml);
        return loadingId;
    },

    /**
     * 隐藏加载动画
     * @param {string} loadingId - 加载ID
     */
    hide(loadingId) {
        if (loadingId) {
            const element = document.getElementById(loadingId);
            if (element) {
                element.remove();
            }
        } else {
            // 移除所有加载动画
            document.querySelectorAll('.loading-overlay').forEach(el => el.remove());
        }
    }
};

/**
 * 搜索组件
 */
const SearchComponents = {
    /**
     * 创建搜索栏
     * @param {object} options - 配置选项
     * @returns {string} HTML字符串
     */
    createSearchBar(options = {}) {
        const {
            id = 'searchBar',
            placeholder = '请输入关键词搜索...',
            onSearch = null,
            filters = [],
            showAdvanced = false
        } = options;

        let html = '<div class="card mb-3">';
        html += '<div class="card-body">';
        html += '<div class="row g-3 align-items-end">';
        
        // 搜索框
        html += '<div class="col-md-6">';
        html += `<input type="text" class="form-control" id="${id}" placeholder="${placeholder}">`;
        html += '</div>';
        
        // 筛选条件
        if (filters.length > 0) {
            filters.forEach(filter => {
                html += `<div class="col-md-${Math.floor(6 / filters.length)}">`;
                if (filter.type === 'select') {
                    html += FormComponents.createSelect({
                        id: filter.id,
                        label: filter.label,
                        options: filter.options || [],
                        classes: 'mb-0'
                    });
                }
                html += '</div>';
            });
        }
        
        // 搜索按钮
        html += '<div class="col-md-auto">';
        html += '<button type="button" class="btn btn-primary" id="search-btn">';
        html += '<i class="bi bi-search"></i> 搜索';
        html += '</button>';
        if (showAdvanced) {
            html += '<button type="button" class="btn btn-outline-secondary ms-2" id="advanced-search-btn">';
            html += '<i class="bi bi-funnel"></i> 高级搜索';
            html += '</button>';
        }
        html += '</div>';
        
        html += '</div>';
        html += '</div>';
        html += '</div>';
        
        // 绑定搜索事件
        if (onSearch) {
            setTimeout(() => {
                const searchInput = document.getElementById(id);
                const searchBtn = document.getElementById('search-btn');
                
                // 按钮点击
                searchBtn?.addEventListener('click', () => {
                    const keyword = searchInput.value;
                    onSearch(keyword);
                });
                
                // Enter键搜索
                searchInput?.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        const keyword = searchInput.value;
                        onSearch(keyword);
                    }
                });
                
                // 绑定筛选器onChange事件
                if (filters.length > 0) {
                    filters.forEach(filter => {
                        if (filter.onChange) {
                            const filterElement = document.getElementById(filter.id);
                            filterElement?.addEventListener('change', (e) => {
                                filter.onChange(e.target.value);
                            });
                        }
                    });
                }
            }, 100);
        }
        
        return html;
    }
};

/**
 * 选择器组件
 */
const SelectorComponents = {
    /**
     * 显示患者选择弹窗
     * @param {object} options - 配置选项
     * @returns {Promise} 选中的患者对象或null
     */
    async showPatientSelector(options = {}) {
        const {
            title = '选择患者',
            onSelect = null,
            keyword = ''
        } = options;

        return new Promise((resolve) => {
            const modalId = `patient-selector-${Date.now()}`;
            const modalHtml = `
                <div class="modal fade" id="${modalId}" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <!-- 搜索栏 -->
                                <div class="mb-3">
                                    <div class="input-group">
                                        <input type="text" class="form-control" id="patient-selector-search" 
                                               placeholder="请输入患者姓名、身份证号、电话或病历号搜索..." 
                                               value="${keyword}">
                                        <button class="btn btn-primary" type="button" onclick="searchPatientsInSelector()">
                                            <i class="bi bi-search"></i> 搜索
                                        </button>
                                    </div>
                                </div>
                                
                                <!-- 患者列表 -->
                                <div id="patient-selector-list" style="max-height: 400px; overflow-y: auto;">
                                    <div class="text-center p-4">
                                        <div class="loading-spinner"></div>
                                        <p class="mt-2">加载中...</p>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            const modalContainer = document.getElementById('modal-container') || (() => {
                const container = document.createElement('div');
                container.id = 'modal-container';
                document.body.appendChild(container);
                return container;
            })();
            
            modalContainer.insertAdjacentHTML('beforeend', modalHtml);
            
            const modalElement = document.getElementById(modalId);
            const modal = new bootstrap.Modal(modalElement, {
                focus: true,
                keyboard: true
            });
            
            // 等待模态框完全显示后再处理焦点（避免aria-hidden警告）
            modalElement.addEventListener('shown.bs.modal', () => {
                // 模态框完全显示后，确保焦点在模态框内
                const firstInput = modalElement.querySelector('input, textarea, select, button:not([data-bs-dismiss])');
                if (firstInput) {
                    firstInput.focus();
                }
            });
            
            // 加载患者列表
            loadPatientsForSelector(modalId, (patient) => {
                modal.hide();
                if (onSelect) {
                    onSelect(patient);
                }
                resolve(patient);
                modalElement.remove();
            });
            
            // 搜索按钮事件
            window.searchPatientsInSelector = function() {
                const keyword = document.getElementById('patient-selector-search').value;
                loadPatientsForSelector(modalId, (patient) => {
                    modal.hide();
                    if (onSelect) {
                        onSelect(patient);
                    }
                    resolve(patient);
                    modalElement.remove();
                }, keyword);
            };
            
            // Enter键搜索
            document.getElementById('patient-selector-search').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    window.searchPatientsInSelector();
                }
            });
            
            // 关闭时清理
            modalElement.addEventListener('hidden.bs.modal', () => {
                resolve(null);
                delete window.searchPatientsInSelector;
                // 清理存储的患者数据
                delete window[`patients_${modalId}`];
                delete window[`selectPatientInSelectorByIndex_${modalId}`];
                modalElement.remove();
            });
            
            modal.show();
        });
    },

    /**
     * 显示药品选择弹窗
     * @param {object} options - 配置选项
     * @returns {Promise} 选中的药品对象或null
     */
    async showDrugSelector(options = {}) {
        const {
            title = '选择药品',
            onSelect = null,
            keyword = '',
            type = '' // western, tcm, chinese_patent
        } = options;

        return new Promise((resolve) => {
            const modalId = `drug-selector-${Date.now()}`;
            const modalHtml = `
                <div class="modal fade" id="${modalId}" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <!-- 搜索栏和筛选 -->
                                <div class="row mb-3">
                                    <div class="col-md-8">
                                        <input type="text" class="form-control" id="drug-selector-search" 
                                               placeholder="请输入药品名称、编码搜索..." 
                                               value="${keyword}">
                                    </div>
                                    <div class="col-md-4">
                                        <select class="form-select" id="drug-selector-type">
                                            <option value="">全部类型</option>
                                            <option value="western" ${type === 'western' ? 'selected' : ''}>西药</option>
                                            <option value="tcm" ${type === 'tcm' ? 'selected' : ''}>中药</option>
                                            <option value="chinese_patent" ${type === 'chinese_patent' ? 'selected' : ''}>中成药</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <button class="btn btn-primary" type="button" onclick="searchDrugsInSelector()">
                                        <i class="bi bi-search"></i> 搜索
                                    </button>
                                </div>
                                
                                <!-- 药品列表 -->
                                <div id="drug-selector-list" style="max-height: 400px; overflow-y: auto;">
                                    <div class="text-center p-4">
                                        <div class="loading-spinner"></div>
                                        <p class="mt-2">加载中...</p>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            const modalContainer = document.getElementById('modal-container') || (() => {
                const container = document.createElement('div');
                container.id = 'modal-container';
                document.body.appendChild(container);
                return container;
            })();
            
            modalContainer.insertAdjacentHTML('beforeend', modalHtml);
            
            const modalElement = document.getElementById(modalId);
            const modal = new bootstrap.Modal(modalElement, {
                focus: true,
                keyboard: true
            });
            
            // 等待模态框完全显示后再处理焦点（避免aria-hidden警告）
            modalElement.addEventListener('shown.bs.modal', () => {
                // 模态框完全显示后，确保焦点在模态框内
                const firstInput = modalElement.querySelector('input, textarea, select, button:not([data-bs-dismiss])');
                if (firstInput) {
                    firstInput.focus();
                }
            });
            
            // 加载药品列表
            loadDrugsForSelector(modalId, (drug) => {
                modal.hide();
                if (onSelect) {
                    onSelect(drug);
                }
                resolve(drug);
                modalElement.remove();
            });
            
            // 搜索按钮事件
            window.searchDrugsInSelector = function() {
                const keyword = document.getElementById('drug-selector-search').value;
                const type = document.getElementById('drug-selector-type').value;
                loadDrugsForSelector(modalId, (drug) => {
                    modal.hide();
                    if (onSelect) {
                        onSelect(drug);
                    }
                    resolve(drug);
                    modalElement.remove();
                }, keyword, type);
            };
            
            // Enter键搜索
            document.getElementById('drug-selector-search').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    window.searchDrugsInSelector();
                }
            });
            
            // 关闭时清理
            modalElement.addEventListener('hidden.bs.modal', () => {
                resolve(null);
                delete window.searchDrugsInSelector;
                modalElement.remove();
            });
            
            modal.show();
        });
    }
};

/**
 * 加载患者列表供选择器使用
 */
async function loadPatientsForSelector(modalId, onSelect, keyword = '') {
    const container = document.querySelector(`#${modalId} #patient-selector-list`);
    if (!container) return;
    
    try {
        // 调用实际API
        let patients = await PatientAPI.search(keyword);
        
        // 如果API返回的是数组，直接使用；如果是对象，提取items
        if (!Array.isArray(patients)) {
            patients = patients.items || [];
        }
        
        // 模拟数据（如果API返回的数据格式不同，需要适配）
        if (patients.length === 0 && !keyword) {
            // 如果无关键词且无数据，使用默认数据
            patients = [
            {
                id: '1',
                medical_record_no: 'MR20241219001',
                name: '张三',
                gender: 'male',
                age: 35,
                phone: '138****1234',
                id_card: '320***********1234'
            },
            {
                id: '2',
                medical_record_no: 'MR20241219002',
                name: '李四',
                gender: 'female',
                age: 28,
                phone: '139****5678',
                id_card: '320***********5678'
            },
            {
                id: '3',
                medical_record_no: 'MR20241219003',
                name: '王五',
                gender: 'male',
                age: 42,
                phone: '137****9012',
                id_card: '320***********9012'
            }
            ];
        }
        
        // API已返回过滤后的数据，统一字段名（后端返回patient_no，前端使用medical_record_no）
        const filteredPatients = patients.map(patient => {
            // 统一字段名：patient_no -> medical_record_no
            if (patient.patient_no && !patient.medical_record_no) {
                patient.medical_record_no = patient.patient_no;
            }
            return patient;
        });
        
        if (filteredPatients.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> 未找到匹配的患者
                </div>
            `;
            return;
        }
        
        container.innerHTML = filteredPatients.map((patient, index) => {
            // 确保有medical_record_no字段
            const recordNo = patient.medical_record_no || patient.patient_no || '-';
            const patientData = {
                ...patient,
                medical_record_no: recordNo,
                patient_no: recordNo  // 同时保留patient_no字段
            };
            
            // 使用data属性存储患者数据，避免JSON序列化问题
            const patientDataAttr = encodeURIComponent(JSON.stringify(patientData));
            
            return `
            <div class="card mb-2 patient-selector-item" style="cursor: pointer;" 
                 data-patient-index="${index}"
                 data-patient-data="${patientDataAttr}"
                 onclick="selectPatientInSelectorByIndex(${index}, '${modalId}')">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${patient.name || '-'} <span class="badge bg-secondary">${patient.gender === 'male' ? '男' : patient.gender === 'female' ? '女' : '-'}</span> ${patient.age || '-'}岁</h6>
                            <p class="text-muted small mb-0">
                                <span class="me-3">病历号：${recordNo}</span>
                                <span class="me-3">电话：${patient.phone || '-'}</span>
                                <span>身份证：${patient.id_card || '-'}</span>
                            </p>
                        </div>
                        <i class="bi bi-chevron-right"></i>
                    </div>
                </div>
            </div>
        `;
        }).join('');
        
        // 存储患者列表供选择器使用
        window[`patients_${modalId}`] = filteredPatients.map(patient => {
            const recordNo = patient.medical_record_no || patient.patient_no || '-';
            return {
                ...patient,
                medical_record_no: recordNo,
                patient_no: recordNo
            };
        });
        
        // 绑定选择事件（通过索引选择）
        window[`selectPatientInSelectorByIndex_${modalId}`] = function(index) {
            const patients = window[`patients_${modalId}`];
            if (!patients || !patients[index]) {
                console.error('患者数据未找到，索引:', index);
                return;
            }
            
            const patient = patients[index];
            // 确保字段名统一
            const patientData = {
                ...patient,
                medical_record_no: patient.medical_record_no || patient.patient_no || '-',
                patient_no: patient.patient_no || patient.medical_record_no || '-'
            };
            
            onSelect(patientData);
        };
        
        // 全局选择函数（兼容旧代码）
        window.selectPatientInSelectorByIndex = function(index, modalId) {
            if (window[`selectPatientInSelectorByIndex_${modalId}`]) {
                window[`selectPatientInSelectorByIndex_${modalId}`](index);
            }
        };
        
    } catch (error) {
        console.error('加载患者列表失败:', error);
        container.innerHTML = '<div class="alert alert-danger">加载失败，请刷新重试</div>';
    }
}

/**
 * 加载药品列表供选择器使用
 */
async function loadDrugsForSelector(modalId, onSelect, keyword = '', type = '') {
    const container = document.querySelector(`#${modalId} #drug-selector-list`);
    if (!container) return;
    
    try {
        // 调用实际API
        const response = await PharmacyAPI.getDrugs({ keyword, type, page_size: 50 });
        let drugs = response.items || response || [];
        
        // 确保是数组
        if (!Array.isArray(drugs)) {
            drugs = [];
        }
        
        // 模拟数据（如果API返回的数据格式不同，需要适配）
        if (drugs.length === 0 && !keyword && !type) {
            // 如果无关键词且无数据，使用默认数据
            drugs = [
            {
                id: '1',
                name: '阿莫西林胶囊',
                code: 'DRUG001',
                type: 'western',
                specification: '0.25g*24粒',
                unit: '盒',
                price: 25.00,
                stock: 150
            },
            {
                id: '2',
                name: '板蓝根颗粒',
                code: 'DRUG002',
                type: 'chinese_patent',
                specification: '10g*20袋',
                unit: '盒',
                price: 18.50,
                stock: 80
            },
            {
                id: '3',
                name: '黄芪',
                code: 'DRUG003',
                type: 'tcm',
                specification: '500g',
                unit: '袋',
                price: 45.00,
                stock: 20
            },
            {
                id: '4',
                name: '感冒灵颗粒',
                code: 'DRUG004',
                type: 'chinese_patent',
                specification: '10g*9袋',
                unit: '盒',
                price: 28.50,
                stock: 100
            }
            ];
        }
        
        // API已返回过滤后的数据，直接使用
        const filteredDrugs = drugs;
        
        if (filteredDrugs.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> 未找到匹配的药品
                </div>
            `;
            return;
        }
        
        container.innerHTML = filteredDrugs.map(drug => {
            const typeMap = {
                'western': { text: '西药', class: 'badge bg-info' },
                'tcm': { text: '中药', class: 'tcm-badge' },
                'chinese_patent': { text: '中成药', class: 'badge bg-success' }
            };
            const typeInfo = typeMap[drug.type] || { text: drug.type, class: 'badge bg-secondary' };
            
            return `
                <div class="card mb-2 drug-selector-item" style="cursor: pointer;" 
                     onclick="selectDrugInSelector('${drug.id}', ${JSON.stringify(drug).replace(/"/g, '&quot;')})">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="flex-grow-1">
                                <h6 class="mb-1">
                                    ${drug.name} 
                                    <span class="${typeInfo.class}">${typeInfo.text}</span>
                                    ${drug.stock < 50 ? '<span class="badge bg-warning">库存低</span>' : ''}
                                </h6>
                                <p class="text-muted small mb-0">
                                    <span class="me-3">编码：${drug.code}</span>
                                    <span class="me-3">规格：${drug.specification}</span>
                                    <span class="me-3">单位：${drug.unit}</span>
                                    <span class="me-3">单价：${utils.formatMoney(drug.price)}</span>
                                    <span>库存：${drug.stock}</span>
                                </p>
                            </div>
                            <i class="bi bi-chevron-right"></i>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // 绑定选择事件
        window.selectDrugInSelector = function(drugId, drug) {
            onSelect(drug);
        };
        
    } catch (error) {
        console.error('加载药品列表失败:', error);
        container.innerHTML = '<div class="alert alert-danger">加载失败，请刷新重试</div>';
    }
}

// 导出组件
window.FormComponents = FormComponents;
window.TableComponents = TableComponents;
window.ModalComponents = ModalComponents;
window.LoadingComponents = LoadingComponents;
window.SearchComponents = SearchComponents;
window.SelectorComponents = SelectorComponents;

