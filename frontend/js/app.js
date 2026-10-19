/**
 * 门诊诊所管理系统 - 主应用入口
 * 
 * 功能：
 * - 应用初始化
 * - 路由管理
 * - 全局状态管理
 * - API调用封装
 */

// 应用配置
const APP_CONFIG = {
    API_BASE_URL: '/api/v1',
    TOKEN_KEY: 'his_token',
    USER_KEY: 'his_user',
    PROJECT_NAME: '华宣诊所管理系统', // 默认值，将从后端API获取
    ROUTES: {
        login: '/login.html',
        platformLogin: '/platform-login.html',
        dashboard: '/views/dashboard.html',
        platformDashboard: '/views/platform/dashboard.html',
        patients: '/views/patients/list.html',
        registrations: '/views/registrations/list.html',
        treatments: '/views/treatments/list.html',
        payments: '/views/payments/list.html',
        pharmacy: '/views/pharmacy/list.html',
        reports: '/views/reports/list.html',
        system: '/views/system/users.html',
        platformTenants: '/views/platform/tenants.html'
    }
};

// 应用主类
class App {
    constructor() {
        this.currentUser = null;
        this.currentRoute = null;
        this.init();
    }

    /**
     * 初始化应用
     */
    async init() {
        // 从后端获取项目配置
        await this.loadAppConfig();
        
        // 检查登录状态
        this.checkAuth();
        
        // 初始化路由
        this.initRouter();
        
        // 绑定全局事件
        this.bindEvents();
        
        // 加载当前页面
        this.loadPage();
    }

    /**
     * 从后端加载应用配置（项目名称等）
     */
    async loadAppConfig() {
        try {
            const response = await fetch('/api');
            if (response.ok) {
                const data = await response.json();
                if (data.code === 200 && data.data && data.data.project_name) {
                    APP_CONFIG.PROJECT_NAME = data.data.project_name;
                }
            }
        } catch (error) {
            console.warn('加载应用配置失败，使用默认值:', error);
        }
    }

    /**
     * 检查认证状态
     */
    checkAuth() {
        const token = localStorage.getItem(APP_CONFIG.TOKEN_KEY);
        const user = localStorage.getItem(APP_CONFIG.USER_KEY);
        
        if (token) {
            // 只要 token 存在即视为已登录；his_user 可能尚未写入（如切换租户后），
            // 由 renderMainLayout -> refreshUserInfo 从 /auth/me 异步补齐，避免登录页与首页互跳
            this.currentUser = user ? JSON.parse(user) : null;
            // 初始化权限管理器
            if (window.permissionManager) {
                window.permissionManager.init(this.currentUser);
            }
            // 如果不在登录页，显示主界面
            if (!window.location.pathname.includes('login')) {
                this.renderMainLayout();
            }
        } else {
            // 未登录，跳转到登录页
            if (!window.location.pathname.includes('login')) {
                window.location.href = APP_CONFIG.ROUTES.login;
            }
        }
    }

    /**
     * 初始化路由
     */
    initRouter() {
        // 简单的路由处理
        const path = window.location.pathname;
        const hash = window.location.hash;
        const search = window.location.search;
        
        if (hash) {
            // 支持hash路由，如 #patients/detail?id=123
            this.currentRoute = hash.substring(1) + search;
        } else if (path.includes('login')) {
            this.currentRoute = 'login';
        } else if (path.includes('patients/detail')) {
            this.currentRoute = 'patients/detail' + search;
        } else if (path.includes('patients/edit')) {
            this.currentRoute = 'patients/edit' + search;
        } else if (path.includes('treatments/edit')) {
            this.currentRoute = 'treatments/edit' + search;
        } else if (path.includes('treatments/detail')) {
            this.currentRoute = 'treatments/detail' + search;
        } else {
            this.currentRoute = 'dashboard';
        }
    }

    /**
     * 绑定全局事件
     */
    bindEvents() {
        // 侧边栏折叠/展开
        document.addEventListener('click', (e) => {
            // 检查点击的是按钮本身或其子元素（如图标）
            const toggleBtn = e.target.closest('.sidebar-toggle');
            if (toggleBtn) {
                e.preventDefault();
                e.stopPropagation();
                this.toggleSidebar();
            }
        });

        // 菜单项点击
        document.addEventListener('click', (e) => {
            if (e.target.closest('.menu-item')) {
                const menuItem = e.target.closest('.menu-item');
                const route = menuItem.dataset.route;
                if (route) {
                    this.navigate(route);
                }
            }
        });

        // 登出
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('logout-btn')) {
                this.logout();
            }
        });
    }

    /**
     * 渲染主布局
     */
    renderMainLayout() {
        const appContainer = document.getElementById('app');
        if (!appContainer) return;

        appContainer.innerHTML = `
            <!-- Header -->
            <header class="app-header">
                <div class="d-flex align-items-center">
                    <button class="btn btn-link sidebar-toggle d-md-none" type="button">
                        <i class="bi bi-list"></i>
                    </button>
                    <div class="logo">
                        <i class="bi bi-hospital"></i> ${APP_CONFIG.PROJECT_NAME}
                    </div>
                </div>
                <div class="user-info">
                    <span class="d-none d-md-inline" id="header-user-name">用户</span>
                    <div class="dropdown">
                        <button class="btn btn-link dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            <i class="bi bi-person-circle"></i>
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="#" onclick="app.navigate('profile'); return false;"><i class="bi bi-person"></i> 个人中心</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item logout-btn" href="#"><i class="bi bi-box-arrow-right"></i> 退出登录</a></li>
                        </ul>
                    </div>
                </div>
            </header>

            <!-- Sidebar -->
            <aside class="app-sidebar" id="sidebar">
                <nav class="menu" id="sidebar-menu">
                    <!-- 菜单项将根据权限动态渲染 -->
                </nav>
            </aside>

            <!-- Main Content -->
            <main class="app-main" id="main-content">
                <div id="page-content">
                    <!-- 页面内容将动态加载 -->
                </div>
            </main>
        `;

        // 更新用户信息显示
        this.updateUserInfo();
        
        // 从API获取最新的用户信息（包括权限）
        this.refreshUserInfo().then(() => {
            // 渲染菜单（根据权限）
            this.renderMenu();
        }).catch(() => {
            // 如果API调用失败，使用本地存储的用户信息
            this.renderMenu();
        });
        
        // 初始化Bootstrap下拉菜单
        const dropdowns = document.querySelectorAll('.dropdown-toggle');
        dropdowns.forEach(dropdown => {
            new bootstrap.Dropdown(dropdown);
        });

        // 加载页面内容
        this.loadPage();
    }

    /**
     * 渲染菜单（根据权限）
     */
    renderMenu() {
        const menuContainer = document.getElementById('sidebar-menu');
        if (!menuContainer) return;
        
        // 定义菜单项
        const menuItems = [
            { route: 'dashboard', icon: 'bi-speedometer2', label: '工作台' },
            { route: 'patients', icon: 'bi-people', label: '患者管理' },
            { route: 'registrations', icon: 'bi-calendar-check', label: '挂号管理' },
            { route: 'treatments', icon: 'bi-hospital', label: '诊疗管理' },
            { route: 'payments', icon: 'bi-cash-coin', label: '收费管理' },
            { 
                group: true,
                icon: 'bi-capsule',
                label: '药房管理',
                children: [
                    { route: 'pharmacy', icon: 'bi-list-ul', label: '药品管理' },
                    { route: 'pharmacy/dispense', icon: 'bi-capsule', label: '发药' }
                ]
            },
            { 
                group: true,
                icon: 'bi-box-seam',
                label: '进销存管理',
                children: [
                    { route: 'inventory/suppliers', icon: 'bi-truck', label: '供应商管理' },
                    { route: 'inventory/purchase-orders', icon: 'bi-cart-plus', label: '采购单管理' },
                    { route: 'inventory/return-orders', icon: 'bi-arrow-return-left', label: '退货单管理' },
                    { route: 'inventory/transactions', icon: 'bi-list-check', label: '库存流水' },
                    { route: 'inventory/checks', icon: 'bi-clipboard-check', label: '库存盘点' }
                ]
            },
            { route: 'reports', icon: 'bi-bar-chart', label: '报表统计' },
            { route: 'system', icon: 'bi-gear', label: '系统管理' },
            { route: 'system/print-templates', icon: 'bi-printer', label: '打印模板管理' },
            { route: 'system/third-party-configs', icon: 'bi-cloud', label: '第三方服务配置' }
        ];
        
        let menuHtml = '';
        
        console.log('[MENU-DEBUG] renderMenu 开始 | isAdmin =', window.permissionManager ? window.permissionManager.isAdmin() : 'N/A',
            '| userPermissions =', window.permissionManager ? window.permissionManager.getPermissions() : 'N/A');
        menuItems.forEach(item => {
            if (item.group) {
                // 检查是否有任何子菜单项可以访问
                const accessibleChildren = item.children.filter(child => {
                    const ok = window.canAccessMenu ? window.canAccessMenu(child.route) : true;
                    console.log(`[MENU-DEBUG]   子菜单 ${item.label} > ${child.label} (route=${child.route}) => canAccess=${ok}`);
                    return ok;
                });
                
                if (accessibleChildren.length === 0) {
                    console.log(`[MENU-DEBUG]   分组「${item.label}」无可访问子菜单，跳过`);
                    return; // 如果没有可访问的子菜单，不显示分组
                }
                
                menuHtml += `
                    <div class="menu-group">
                        <div class="menu-group-title">
                            <i class="bi ${item.icon}"></i>
                            <span>${item.label}</span>
                        </div>
                `;
                
                accessibleChildren.forEach(child => {
                    if (window.canAccessMenu ? window.canAccessMenu(child.route) : true) {
                        menuHtml += `
                            <a href="#" class="menu-item submenu-item" data-route="${child.route}">
                                <i class="bi ${child.icon}"></i>
                                <span>${child.label}</span>
                            </a>
                        `;
                    }
                });
                
                menuHtml += `</div>`;
            } else {
                // 检查是否可以访问该菜单
                const accessible = window.canAccessMenu ? window.canAccessMenu(item.route) : true;
                console.log(`[MENU-DEBUG]   菜单 ${item.label} (route=${item.route}) => canAccess=${accessible}`);
                if (accessible) {
                    const isActive = this.currentRoute === item.route ? 'active' : '';
                    menuHtml += `
                        <a href="#" class="menu-item ${isActive}" data-route="${item.route}">
                            <i class="bi ${item.icon}"></i>
                            <span>${item.label}</span>
                        </a>
                    `;
                }
            }
        });
        
        menuContainer.innerHTML = menuHtml;
        
        console.log('[MENU-DEBUG] renderMenu 完成 | 渲染菜单数 =', menuContainer.querySelectorAll('.menu-item').length);
        
        // 绑定菜单点击事件
        menuContainer.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const route = item.getAttribute('data-route');
                if (route) {
                    this.navigate(route);
                }
            });
        });
    }

    /**
     * 从API刷新用户信息（包括权限）
     */
    async refreshUserInfo() {
        try {
            if (window.UserAPI && window.UserAPI.getCurrentUserInfo) {
                // 注意：api.js 的 get 已解包为 data.data（即 user_info 对象本身），
                // 因此此处 response 直接就是 user_info，不要再取 .data（否则为 undefined，导致权限未被初始化）
                const userInfo = await window.UserAPI.getCurrentUserInfo();
                if (userInfo) {
                    this.currentUser = userInfo;
                    console.log('[MENU-DEBUG] /auth/me 返回用户数据 |', {
                        username: this.currentUser.username,
                        roles: (this.currentUser.roles || []).map(r => r.code),
                        permissions: this.currentUser.permissions,
                        permissionsCount: (this.currentUser.permissions || []).length
                    });
                    // 更新本地存储
                    localStorage.setItem(APP_CONFIG.USER_KEY, JSON.stringify(this.currentUser));
                    // 重新初始化权限管理器
                    if (window.permissionManager) {
                        window.permissionManager.init(this.currentUser);
                    }
                    // 更新用户信息显示
                    this.updateUserInfo();
                }
            }
        } catch (error) {
            console.warn('刷新用户信息失败，使用本地存储的信息:', error);
        }
    }

    /**
     * 更新用户信息显示
     */
    updateUserInfo() {
        const userNameEl = document.getElementById('header-user-name');
        if (userNameEl && this.currentUser) {
            // 优先显示真实姓名，其次用户名
            const displayName = this.currentUser.real_name || 
                               this.currentUser.name || 
                               this.currentUser.username || 
                               '用户';
            userNameEl.textContent = displayName;
        }
    }
    
    /**
     * 切换侧边栏
     */
    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;
        
        // 检查是否是移动端（屏幕宽度 <= 768px）
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            // 移动端：切换 show 类来控制显示/隐藏
            const isShowing = sidebar.classList.contains('show');
            if (isShowing) {
                sidebar.classList.remove('show');
                // 移除遮罩层
                this.removeSidebarOverlay();
            } else {
                sidebar.classList.add('show');
                // 添加遮罩层
                this.addSidebarOverlay();
            }
        } else {
            // 桌面端：切换 collapsed 类来控制折叠/展开
            sidebar.classList.toggle('collapsed');
        }
    }
    
    /**
     * 添加侧边栏遮罩层（移动端）
     */
    addSidebarOverlay() {
        // 移除已存在的遮罩层
        this.removeSidebarOverlay();
        
        const overlay = document.createElement('div');
        overlay.id = 'sidebar-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 998;
            cursor: pointer;
        `;
        overlay.addEventListener('click', () => {
            this.toggleSidebar();
        });
        document.body.appendChild(overlay);
    }
    
    /**
     * 移除侧边栏遮罩层（移动端）
     */
    removeSidebarOverlay() {
        const overlay = document.getElementById('sidebar-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    /**
     * 导航到指定路由
     */
    navigate(route) {
        // 检查权限
        if (route && window.canAccessMenu && !window.canAccessMenu(route)) {
            if (window.utils && window.utils.showToast) {
                window.utils.showToast('您没有权限访问该页面', 'warning');
            } else {
                alert('您没有权限访问该页面');
            }
            return;
        }
        
        // 更新菜单激活状态（只更新基础路由，忽略查询参数）
        const baseRoute = route ? route.split('?')[0] : route;
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
            const itemRoute = item.getAttribute('data-route');
            if (itemRoute === baseRoute || itemRoute === route) {
                item.classList.add('active');
            }
        });

        // 更新URL hash（如果支持）
        if (route) {
            window.location.hash = '#' + route;
        }

        // 加载页面内容
        this.currentRoute = route;
        this.loadPage();
    }

    /**
     * 加载页面内容
     */
    async loadPage() {
        const contentArea = document.getElementById('page-content');
        if (!contentArea) return;

        // 显示加载状态
        contentArea.innerHTML = '<div class="text-center p-5"><div class="loading-spinner"></div><p class="mt-3">加载中...</p></div>';

        try {
            // 根据路由加载对应页面
            let pagePath = null;
            
            // 如果路由包含查询参数，先提取基础路由
            if (this.currentRoute && this.currentRoute.includes('?')) {
                const [baseRoute, queryString] = this.currentRoute.split('?');
                const basePath = this.getPagePath(baseRoute);
                if (basePath) {
                    pagePath = basePath + '?' + queryString;
                }
            } else {
                pagePath = this.getPagePath(this.currentRoute);
            }
            
            // 调试日志
            console.log('SPA路由加载:', {
                currentRoute: this.currentRoute,
                pagePath: pagePath,
                hasContentArea: !!contentArea
            });
            
            if (pagePath) {
                // 添加时间戳防止缓存
                const cacheBuster = `?t=${Date.now()}`;
                const urlWithCacheBuster = pagePath.includes('?') ? `${pagePath}&_t=${Date.now()}` : `${pagePath}?_t=${Date.now()}`;
                
                console.log('SPA路由: 开始加载页面', { pagePath, urlWithCacheBuster });
                
                const response = await fetch(urlWithCacheBuster);
                
                // 检查响应状态
                if (!response.ok) {
                    console.error('SPA路由: 页面加载失败', {
                        status: response.status,
                        statusText: response.statusText,
                        url: urlWithCacheBuster
                    });
                    if (response.status === 404) {
                        throw new Error(`页面文件未找到: ${pagePath} (${urlWithCacheBuster})`);
                    } else {
                        throw new Error(`加载页面失败: HTTP ${response.status} ${response.statusText}`);
                    }
                }
                
                const html = await response.text();
                console.log('SPA路由: 页面加载成功', { pagePath, htmlLength: html.length });
                
                // 解析HTML，分离内容和脚本
                // 先从原始HTML字符串中提取所有script标签的内容（避免DOMParser截断问题）
                // 使用更精确的匹配方式：先找到所有<script>开始位置，然后找到对应的</script>结束位置
                // 注意：需要跳过在字符串中的</script>（比如模板字符串中的）
                const scriptMatches = [];
                let searchIndex = 0;
                while (true) {
                    const scriptStart = html.indexOf('<script', searchIndex);
                    if (scriptStart === -1) break;
                    
                    // 找到script标签的结束位置（>）
                    const tagEnd = html.indexOf('>', scriptStart);
                    if (tagEnd === -1) break;
                    
                    // 提取属性
                    const attributes = html.substring(scriptStart + 7, tagEnd).trim();
                    
                    // 从>之后开始查找</script>
                    // 需要找到真正的</script>，而不是在字符串中的
                    let contentStart = tagEnd + 1;
                    let scriptEnd = -1;
                    let inString = false;
                    let stringChar = null;
                    
                    // 逐字符查找，跳过字符串中的</script>
                    for (let i = contentStart; i < html.length - 8; i++) {
                        const char = html[i];
                        const next8 = html.substring(i, i + 9);
                        
                        // 检查是否在字符串中
                        if (!inString && (char === '"' || char === "'" || char === '`')) {
                            inString = true;
                            stringChar = char;
                        } else if (inString && char === stringChar) {
                            // 检查是否是转义的引号
                            if (html[i - 1] !== '\\') {
                                inString = false;
                                stringChar = null;
                            }
                        }
                        
                        // 如果不在字符串中，检查是否是</script>
                        if (!inString && next8.toLowerCase() === '</script>') {
                            scriptEnd = i;
                            break;
                        }
                    }
                    
                    if (scriptEnd === -1) break;
                    
                    // 提取内容
                    const content = html.substring(contentStart, scriptEnd);
                    
                    scriptMatches.push({
                        attributes: attributes,
                        content: content,
                        fullMatch: html.substring(scriptStart, scriptEnd + 9)
                    });
                    
                    // 继续搜索下一个script标签
                    searchIndex = scriptEnd + 9;
                }
                
                // 移除所有script标签后再设置innerHTML
                // 使用与提取脚本相同的逻辑来移除script标签，确保一致性
                const tempDiv = document.createElement('div');
                let htmlContent = html;
                
                // 使用与提取脚本相同的逻辑：跳过字符串中的</script>
                // 但这里我们需要移除所有script标签，包括在字符串中的
                // 所以使用更简单但有效的方法：基于已提取的scriptMatches来移除
                scriptMatches.forEach(scriptMatch => {
                    htmlContent = htmlContent.replace(scriptMatch.fullMatch, '');
                });
                
                // 如果还有遗漏的script标签（比如在字符串中的），使用正则表达式移除
                // 但要注意：这个正则可能会误删，所以只在有遗漏时使用
                htmlContent = htmlContent.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '');
                
                tempDiv.innerHTML = htmlContent;
                contentArea.innerHTML = tempDiv.innerHTML;
                
                // 执行脚本（延迟执行，确保DOM已更新）
                setTimeout(() => {
                    scriptMatches.forEach((scriptMatch, index) => {
                        const script = {
                            src: null,
                            textContent: scriptMatch.content,
                            innerHTML: scriptMatch.content
                        };
                        
                        // 解析script标签的属性
                        const attrs = scriptMatch.attributes;
                        if (attrs) {
                            const srcMatch = attrs.match(/src\s*=\s*["']([^"']+)["']/i);
                            if (srcMatch) {
                                script.src = srcMatch[1];
                            }
                        }
                        try {
                            if (script.src) {
                                // 外部脚本 - 跳过已在index.html中加载的脚本，避免重复加载
                                const scriptSrc = script.src;
                                // 检查是否是已加载的公共脚本
                                const isCommonScript = scriptSrc.includes('/js/components.js') ||
                                                       scriptSrc.includes('/js/error-handler.js') ||
                                                       scriptSrc.includes('/js/api.js') ||
                                                       scriptSrc.includes('/js/utils.js') ||
                                                       scriptSrc.includes('bootstrap.bundle.min.js');
                                
                                if (isCommonScript) {
                                    // 公共脚本已在index.html中加载，跳过
                                    console.log(`跳过已加载的公共脚本: ${scriptSrc}`);
                                    return;
                                }
                                
                                // 检查是否已存在
                                const existingScript = document.querySelector(`script[src="${scriptSrc}"]`);
                                if (!existingScript) {
                                    const newScript = document.createElement('script');
                                    newScript.src = scriptSrc;
                                    newScript.async = false;
                                    // 等待脚本加载完成后再继续
                                    newScript.onload = () => {
                                        console.log(`外部脚本加载完成: ${scriptSrc}`);
                                    };
                                    newScript.onerror = () => {
                                        console.error(`外部脚本加载失败: ${scriptSrc}`);
                                    };
                                    document.head.appendChild(newScript);
                                } else {
                                    console.log(`脚本已加载，跳过: ${scriptSrc}`);
                                }
                            } else if (script.textContent || script.innerHTML) {
                                // 内联脚本
                                // 优先使用textContent，如果为空则使用innerHTML
                                const scriptContent = (script.textContent || script.innerHTML || '').trim();
                                if (scriptContent) {
                                    // 检查脚本内容是否完整（避免截断导致的语法错误）
                                    // 简单检查：如果内容以不完整的引号或括号结尾，可能是截断了
                                    // 但要注意：模板字符串中的反引号可能影响检查，所以放宽检查条件
                                    const quoteCount = (scriptContent.match(/['"]/g) || []).length;
                                    const backtickCount = (scriptContent.match(/`/g) || []).length;
                                    const parenCount = (scriptContent.match(/\(/g) || []).length;
                                    const closeParenCount = (scriptContent.match(/\)/g) || []).length;
                                    const braceCount = (scriptContent.match(/\{/g) || []).length;
                                    const closeBraceCount = (scriptContent.match(/\}/g) || []).length;
                                    const bracketCount = (scriptContent.match(/\[/g) || []).length;
                                    const closeBracketCount = (scriptContent.match(/\]/g) || []).length;
                                    
                                    // 放宽检查：只检查括号和花括号是否匹配
                                    // 注意：模板字符串中的反引号可能成对出现，所以不严格检查引号匹配
                                    // 只要括号和花括号匹配，且不以引号结尾，就认为是完整的
                                    const isComplete = parenCount === closeParenCount &&
                                                      braceCount === closeBraceCount &&
                                                      bracketCount === closeBracketCount &&
                                                      !scriptContent.match(/['"`]$/); // 不以引号结尾
                                    
                                    // 如果脚本内容很长（超过500字符），即使检查失败也尝试执行（可能是误判）
                                    // 或者如果脚本包含常见的函数定义模式，也尝试执行
                                    const hasFunctionPattern = /function\s+\w+|=>\s*\{|window\.\w+\s*=\s*function|window\.\w+\s*=\s*async\s+function/.test(scriptContent);
                                    
                                    if (!isComplete && (scriptContent.length > 500 || hasFunctionPattern)) {
                                        console.warn('脚本完整性检查失败，但内容较长或包含函数定义，尝试执行:', scriptContent.substring(0, 100));
                                        // 不return，继续执行
                                    } else if (!isComplete) {
                                        console.warn('检测到可能不完整的脚本内容，跳过执行:', scriptContent.substring(0, 100));
                                        console.warn('脚本完整性检查详情:', {
                                            parenCount, closeParenCount,
                                            braceCount, closeBraceCount,
                                            bracketCount, closeBracketCount,
                                            quoteCount, backtickCount,
                                            endsWithQuote: !!scriptContent.match(/['"`]$/),
                                            contentLength: scriptContent.length,
                                            hasFunctionPattern: hasFunctionPattern
                                        });
                                        return;
                                    }
                                    
                                    // 使用Function构造器执行，避免appendChild的问题
                                    try {
                                        // 检查脚本是否以分号或花括号结尾（基本完整性检查）
                                        const trimmedContent = scriptContent.trim();
                                        const endsProperly = /[;})]$/.test(trimmedContent);
                                        if (!endsProperly && scriptContent.length < 100) {
                                            console.warn('脚本可能不完整（长度短且不以分号或花括号结尾），跳过执行');
                                            console.warn('脚本结尾:', trimmedContent.substring(Math.max(0, trimmedContent.length - 50)));
                                            return;
                                        }
                                        
                                        // 语法验证：检查 try-catch-finally 的完整性
                                        const tryCount = (scriptContent.match(/\btry\s*\{/g) || []).length;
                                        const catchCount = (scriptContent.match(/\bcatch\s*\(/g) || []).length;
                                        const finallyCount = (scriptContent.match(/\bfinally\s*\{/g) || []).length;
                                        
                                        // 每个 try 必须有对应的 catch 或 finally
                                        if (tryCount > 0 && tryCount > (catchCount + finallyCount)) {
                                            const errorMsg = `语法错误：检测到 ${tryCount} 个 try 语句，但只有 ${catchCount} 个 catch 和 ${finallyCount} 个 finally。每个 try 必须有对应的 catch 或 finally。`;
                                            console.error(errorMsg);
                                            console.error('脚本内容（前500字符）:', scriptContent.substring(0, 500));
                                            console.error('脚本内容长度:', scriptContent.length);
                                            
                                            // 尝试定位问题位置
                                            const tryMatches = [...scriptContent.matchAll(/\btry\s*\{/g)];
                                            tryMatches.forEach((match, index) => {
                                                const lineNum = scriptContent.substring(0, match.index).split('\n').length;
                                                console.error(`Try 语句 #${index + 1} 位置: 第 ${lineNum} 行附近`);
                                            });
                                            
                                            throw new SyntaxError(errorMsg);
                                        }
                                        
                                        // 对于长脚本，添加调试信息
                                        if (scriptContent.length > 1000) {
                                            console.log(`执行长脚本 (${scriptContent.length} 字符)`);
                                        }
                                        
                                        // 使用 Function 构造器进行语法检查（不执行）
                                        try {
                                            new Function(scriptContent);
                                        } catch (syntaxError) {
                                            if (syntaxError instanceof SyntaxError) {
                                                console.error('脚本语法错误:', syntaxError.message);
                                                console.error('脚本内容（前500字符）:', scriptContent.substring(0, 500));
                                                console.error('脚本内容长度:', scriptContent.length);
                                                console.error('脚本结尾（最后100字符）:', scriptContent.substring(Math.max(0, scriptContent.length - 100)));
                                                throw syntaxError;
                                            }
                                        }
                                        
                                        // 语法检查通过，执行脚本
                                        const func = new Function(scriptContent);
                                        func();
                                    } catch (e) {
                                        console.error('执行脚本失败:', e);
                                        console.error('脚本内容（前500字符）:', scriptContent.substring(0, 500));
                                        console.error('脚本内容长度:', scriptContent.length);
                                        console.error('脚本结尾（最后100字符）:', scriptContent.substring(Math.max(0, scriptContent.length - 100)));
                                        
                                        // 提供修复建议
                                        if (e instanceof SyntaxError) {
                                            if (e.message.includes('try')) {
                                                console.error('修复建议：检查所有 try 语句是否有对应的 catch 或 finally 块');
                                            } else if (e.message.includes('Missing catch or finally')) {
                                                console.error('修复建议：每个 try 语句必须有对应的 catch 或 finally 块');
                                            } else {
                                                console.error('修复建议：检查脚本语法，确保所有括号、花括号、引号都正确匹配');
                                            }
                                        }
                                        
                                        // 如果Function构造器失败，不再尝试eval（避免执行有问题的代码）
                                        // 只在开发环境提供更详细的错误信息
                                        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                                            console.error('提示：这是开发环境，请修复脚本语法错误后再继续');
                                        }
                                    }
                                }
                            }
                        } catch (error) {
                            console.error('处理脚本时出错:', error, scriptMatch);
                        }
                    });
                }, 0);
                
                // 更新window.location.search以支持页面内获取参数
                if (this.currentRoute && this.currentRoute.includes('?')) {
                    const queryString = this.currentRoute.split('?')[1];
                    // 使用history API更新URL，但不刷新页面
                    if (window.history && window.history.replaceState) {
                        // 获取当前hash，移除已有的查询参数
                        let hash = window.location.hash || '';
                        // 如果hash中已经包含查询参数，先移除
                        if (hash.includes('?')) {
                            hash = hash.split('?')[0];
                        }
                        // 构建新的URL：pathname + hash + 查询参数
                        const newUrl = window.location.pathname + hash + '?' + queryString;
                        window.history.replaceState(null, '', newUrl);
                        console.log('SPA路由: 已更新URL参数', newUrl);
                    }
                }
                
                // 执行页面特定脚本
                // 延迟执行，确保DOM已更新和脚本已执行
                setTimeout(() => {
                    this.initPageScripts(this.currentRoute);
                }, 100);
            } else {
                contentArea.innerHTML = '<div class="alert alert-danger">页面未找到</div>';
            }
        } catch (error) {
            console.error('加载页面失败:', error);
            contentArea.innerHTML = `
                <div class="alert alert-danger">
                    <h5>加载页面失败</h5>
                    <p>${error.message || '未知错误'}</p>
                    <button class="btn btn-primary mt-2" onclick="location.reload()">刷新页面</button>
                </div>
            `;
        }
    }

    /**
     * 获取页面路径
     */
    getPagePath(route) {
        // 如果route为null或undefined，返回null
        if (!route) {
            // 静默处理，避免过多警告日志
            return null;
        }
        
        const routeMap = {
            'dashboard': '/views/dashboard.html',
            'patients': '/views/patients/list.html',
            'patients/detail': '/views/patients/detail.html',
            'patients/edit': '/views/patients/edit.html',
            'registrations': '/views/registrations/list.html',
            'treatments': '/views/treatments/list.html',
            'treatments/edit': '/views/treatments/edit.html',
            'treatments/detail': '/views/treatments/detail.html',
            'payments': '/views/payments/list.html',
            'payments/bill-detail': '/views/payments/bill-detail.html',
            'pharmacy': '/views/pharmacy/list.html',
            'pharmacy/dispense': '/views/pharmacy/dispense.html',
            'reports': '/views/reports/list.html',
            'system': '/views/system/users.html',
            'profile': '/views/profile.html',
            'schedules': '/views/registrations/schedules.html',
            'prescriptions': '/views/treatments/prescriptions.html',
            'treatments/prescription-detail': '/views/treatments/prescription-detail.html',
            'inventory-warning': '/views/pharmacy/warning.html',
            'roles': '/views/system/roles.html',
            'departments': '/views/system/departments.html',
            'doctors': '/views/system/doctors.html',
            'system/print-templates': '/views/system/print-templates.html',
            'system/print-templates/editor': '/views/system/print-templates-editor.html',
            'system/third-party-configs': '/views/system/third-party-configs.html',
            'system/settings': '/views/system/settings.html',
            'inventory/suppliers': '/views/inventory/suppliers.html',
            'inventory/purchase-orders': '/views/inventory/purchase-orders.html',
            'inventory/return-orders': '/views/inventory/return-orders.html',
            'inventory/transactions': '/views/inventory/transactions.html',
            'inventory/checks': '/views/inventory/checks.html'
        };
        
        // 支持带参数的路径，如 patients/detail?id=xxx
        if (typeof route === 'string' && route.includes('?')) {
            const [baseRoute, queryString] = route.split('?');
            console.log('getPagePath: 带参数路由', { route, baseRoute, queryString });
            if (routeMap[baseRoute]) {
                const fullPath = routeMap[baseRoute] + '?' + queryString;
                console.log('getPagePath: 返回路径', fullPath);
                return fullPath;
            } else {
                console.warn('getPagePath: 基础路由未找到', baseRoute);
            }
        }
        
        const path = routeMap[route] || null;
        console.log('getPagePath: 路由映射', { route, path, hasPath: !!path });
        return path;
    }

    /**
     * 初始化页面特定脚本
     */
    initPageScripts(route) {
        // 根据路由执行对应的初始化脚本
        // 这里可以在各个页面中定义自己的初始化逻辑
        try {
            console.log('initPageScripts: 初始化页面脚本', { route, hasPageInit: typeof window.pageInit === 'function' });
            if (window.pageInit && typeof window.pageInit === 'function') {
                window.pageInit();
            } else {
                console.warn('initPageScripts: window.pageInit未定义或不是函数');
            }
            
            // 初始化搜索栏（如果存在）
            if (window.initSearchBar && typeof window.initSearchBar === 'function') {
                // 延迟执行，确保DOM已完全加载
                setTimeout(() => {
                    try {
                        const container = document.getElementById('search-container');
                        if (container) {
                            window.initSearchBar();
                        } else {
                            // search-container元素不存在时，静默跳过（某些页面可能不需要搜索栏）
                            // console.warn('search-container元素未找到，跳过搜索栏初始化');
                        }
                    } catch (error) {
                        console.error('初始化搜索栏失败:', error);
                    }
                }, 100);
            }
        } catch (error) {
            console.error('初始化页面脚本失败:', error);
        }
    }

    /**
     * 登出
     */
    async logout() {
        if (!confirm('确定要退出登录吗？')) {
            return;
        }
        
        try {
            // 调用登出API
            const currentToken = localStorage.getItem(APP_CONFIG.TOKEN_KEY);
            if (currentToken && typeof window.api !== 'undefined') {
                try {
                    await window.api.post('/auth/logout');
                } catch (error) {
                    console.warn('调用登出API失败（继续清除本地数据）:', error);
                }
            }
        } catch (error) {
            console.warn('登出API调用失败（继续清除本地数据）:', error);
        }
        
        // 清除本地存储
        localStorage.removeItem(APP_CONFIG.TOKEN_KEY);
        localStorage.removeItem('his_refresh_token');
        localStorage.removeItem(APP_CONFIG.USER_KEY);
        
        // 跳转到登录页面
        window.location.href = APP_CONFIG.ROUTES.login;
    }
}

// API调用封装
class ApiClient {
    /**
     * 发送HTTP请求
     * @param {string} url - 请求URL
     * @param {object} options - 请求选项
     * @returns {Promise} 响应数据
     */
    async request(url, options = {}) {
        const token = localStorage.getItem(APP_CONFIG.TOKEN_KEY);
        
        // 判断是否为FormData，如果是则不要设置Content-Type（让浏览器自动设置）
        const isFormData = options.body instanceof FormData;
        
        const defaultOptions = {
            headers: {
                ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };

        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...(options.headers || {})
            }
        };

        try {
            const response = await fetch(`${APP_CONFIG.API_BASE_URL}${url}`, config);
            
            // 处理401未授权错误（token过期）
            if (response.status === 401) {
                // 尝试刷新token
                try {
                    const refreshResponse = await fetch(`${APP_CONFIG.API_BASE_URL}/auth/refresh`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            ...(token && { 'Authorization': `Bearer ${token}` })
                        }
                    });
                    
                    if (refreshResponse.ok) {
                        const refreshData = await refreshResponse.json();
                        if (refreshData.code === 200 && refreshData.data.token) {
                            localStorage.setItem(APP_CONFIG.TOKEN_KEY, refreshData.data.token);
                            // 重试原请求
                            config.headers['Authorization'] = `Bearer ${refreshData.data.token}`;
                            const retryResponse = await fetch(`${APP_CONFIG.API_BASE_URL}${url}`, config);
                            if (!retryResponse.ok) {
                                const errorData = await retryResponse.json().catch(() => ({}));
                                const error = new Error(errorData.message || `HTTP error! status: ${retryResponse.status}`);
                                error.response = { data: errorData, status: retryResponse.status };
                                throw error;
                            }
                            return await retryResponse.json();
                        }
                    }
                } catch (refreshError) {
                    console.error('刷新token失败:', refreshError);
                }
                
                // 刷新失败，清除token并跳转到登录页
                localStorage.removeItem(APP_CONFIG.TOKEN_KEY);
                localStorage.removeItem(APP_CONFIG.USER_KEY);
                if (!window.location.pathname.includes('login')) {
                    if (window.ErrorHandler) {
                        ErrorHandler.showError('登录已过期，请重新登录', { title: '认证失败' });
                    }
                    setTimeout(() => {
                        window.location.href = APP_CONFIG.ROUTES.login;
                    }, 2000);
                }
                const error = new Error('登录已过期，请重新登录');
                error.response = { status: 401 };
                throw error;
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                
                // 处理422验证错误，显示详细的验证错误信息
                if (response.status === 422) {
                    let errorMessage = errorData.message || '请求数据验证失败';
                    
                    // FastAPI的默认验证错误格式是 {detail: [...]}
                    // 我们的自定义格式是 {data: {details: {errors: [...]}}}
                    let validationErrors = null;
                    
                    if (errorData.detail && Array.isArray(errorData.detail)) {
                        // FastAPI默认格式
                        validationErrors = errorData.detail;
                        const errorDetails = validationErrors.map(err => {
                            const field = err.loc && err.loc.length > 0 ? err.loc[err.loc.length - 1] : '未知字段';
                            const msg = err.msg || '验证失败';
                            return `${field}: ${msg}`;
                        }).join('; ');
                        errorMessage = `请求数据验证失败: ${errorDetails}`;
                    } else if (errorData.data && errorData.data.details) {
                        // 我们的自定义格式
                        if (errorData.data.details.errors) {
                            validationErrors = errorData.data.details.errors;
                            const errorDetails = validationErrors.map(err => {
                                const field = err.loc ? err.loc.join('.') : '未知字段';
                                const msg = err.msg || '验证失败';
                                return `${field}: ${msg}`;
                            }).join('; ');
                            errorMessage = `${errorMessage}\n详细错误: ${errorDetails}`;
                        }
                    }
                    
                    const error = new Error(errorMessage);
                    error.response = { data: errorData, status: response.status };
                    error.code = 422;
                    error.validationErrors = validationErrors; // 保存验证错误以便后续使用
                    throw error;
                }
                
                const error = new Error(errorData.message || `HTTP error! status: ${response.status}`);
                error.response = { data: errorData, status: response.status };
                throw error;
            }

            const data = await response.json();
            
            // 处理后端响应格式 {code, message, data, timestamp}
            if (data.code !== 200) {
                // API返回错误
                const error = new Error(data.message || '请求失败');
                error.code = data.code;
                error.data = data.data;
                error.response = { data: data, status: response.status };
                
                // 如果是401未授权错误，触发登录跳转
                if (data.code === 401 || response.status === 401) {
                    localStorage.removeItem(APP_CONFIG.TOKEN_KEY);
                    localStorage.removeItem(APP_CONFIG.USER_KEY);
                    if (!window.location.pathname.includes('login')) {
                        if (window.ErrorHandler) {
                            ErrorHandler.showError('登录已过期，请重新登录', { title: '认证失败' });
                        }
                        setTimeout(() => {
                            window.location.href = APP_CONFIG.ROUTES.login;
                        }, 2000);
                    }
                }
                
                throw error;
            }
            
            // 返回data字段（后端统一返回格式）
            return data.data || data;
        } catch (error) {
            console.error('API请求失败:', error);
            // 使用错误处理器显示错误
            if (window.ErrorHandler && error.response) {
                ErrorHandler.handleApiError(error);
            }
            throw error;
        }
    }

    /**
     * GET请求
     */
    get(url, params = {}) {
        // 过滤掉空值和undefined
        const cleanParams = {};
        for (const [key, value] of Object.entries(params)) {
            if (value !== null && value !== undefined && value !== '') {
                cleanParams[key] = value;
            }
        }
        const queryString = new URLSearchParams(cleanParams).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        return this.request(fullUrl, { method: 'GET' });
    }

    /**
     * POST请求
     */
    post(url, data = {}) {
        // 如果是FormData，直接传递，否则序列化为JSON
        const body = data instanceof FormData ? data : JSON.stringify(data);
        return this.request(url, {
            method: 'POST',
            body: body
        });
    }

    /**
     * PUT请求
     */
    put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE请求
     */
    delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
}

// 工具函数
const Utils = {
    /**
     * 显示Toast通知（已废弃，使用ErrorHandler.showToast）
     * @deprecated 使用 ErrorHandler.showToast 代替
     */
    showToast(message, type = 'info') {
        if (window.ErrorHandler) {
            ErrorHandler.showToast(message, type);
        } else {
            console.warn('ErrorHandler未加载，使用默认Toast');
            const toastContainer = document.querySelector('.toast-container') || this.createToastContainer();
            
            const toast = document.createElement('div');
            toast.className = `toast align-items-center text-white bg-${type} border-0`;
            toast.setAttribute('role', 'alert');
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;
            
            toastContainer.appendChild(toast);
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        }
    },

    /**
     * 创建Toast容器
     */
    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    },

    /**
     * 格式化日期
     */
    formatDate(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },

    /**
     * 格式化金额
     */
    formatMoney(amount) {
        return `¥${Number(amount).toFixed(2)}`;
    }
};

// 全局API客户端
const api = new ApiClient();

// 立即导出到全局，供其他脚本使用
window.api = api;
window.utils = Utils;

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

