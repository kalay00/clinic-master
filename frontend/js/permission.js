/**
 * 权限管理模块
 * 提供统一的权限检查功能
 */

/**
 * 菜单权限映射
 * 定义每个菜单项所需的权限
 */
const MENU_PERMISSIONS = {
    'dashboard': [], // 工作台，所有用户都可以访问
    'patients': ['patient:list'], // 患者管理
    'registrations': ['registration:list'], // 挂号管理
    'treatments': ['treatment:list'], // 诊疗管理
    'payments': ['payment:list'], // 收费管理
    'pharmacy': ['pharmacy:list'], // 药房管理
    'pharmacy/dispense': ['pharmacy:dispense'], // 发药
    'inventory/suppliers': ['inventory:list'], // 供应商管理
    'inventory/purchase-orders': ['inventory:list'], // 采购单管理
    'inventory/return-orders': ['inventory:list'], // 退货单管理
    'inventory/transactions': ['inventory:list'], // 库存流水
    'inventory/checks': ['inventory:list'], // 库存盘点
    'reports': ['report:list'], // 报表统计
    'system': ['system:list'], // 系统管理
    'system/print-templates': ['print_template:list'], // 打印模板管理
    'system/third-party-configs': ['system:list'], // 第三方服务配置
    'roles': ['role:list'], // 角色权限管理
};

/**
 * 功能权限映射
 * 定义每个功能按钮所需的权限
 */
const FUNCTION_PERMISSIONS = {
    // 患者管理
    'patient:create': ['patient:create'],
    'patient:update': ['patient:update'],
    'patient:delete': ['patient:delete'],
    
    // 挂号管理
    'registration:create': ['registration:create'],
    'registration:update': ['registration:update'],
    'registration:delete': ['registration:delete'],
    
    // 诊疗管理
    'treatment:create': ['treatment:create'],
    'treatment:update': ['treatment:update'],
    'treatment:delete': ['treatment:delete'],
    
    // 收费管理
    'payment:create': ['payment:create'],
    'payment:update': ['payment:update'],
    'payment:delete': ['payment:delete'],
    
    // 药房管理
    'pharmacy:dispense': ['pharmacy:dispense'],
    'pharmacy:create': ['pharmacy:create'],
    'pharmacy:update': ['pharmacy:update'],
    'pharmacy:delete': ['pharmacy:delete'],
    
    // 系统管理
    'system:user:create': ['system:user:create'],
    'system:user:update': ['system:user:update'],
    'system:user:delete': ['system:user:delete'],
    'system:role:create': ['system:role:create'],
    'system:role:update': ['system:role:update'],
    'system:role:delete': ['system:role:delete'],
};

/**
 * 权限检查器
 */
class PermissionManager {
    constructor() {
        this.currentUser = null;
        this.userPermissions = [];
        this.userRoles = [];
    }

    /**
     * 初始化权限管理器
     * @param {Object} user - 用户信息
     */
    init(user) {
        this.currentUser = user;

        // user 可能尚未就绪（如切换租户后 his_user 未写入，待 /auth/me 异步补齐后会再次 init）
        // 此处做空值保护，避免读取 null.permissions 抛错中断初始化
        if (!user) {
            this.userPermissions = [];
            this.userRoles = [];
            return;
        }

        // 提取权限列表
        if (user.permissions && Array.isArray(user.permissions)) {
            this.userPermissions = user.permissions.map(p => {
                if (typeof p === 'string') {
                    return p;
                } else if (p.code) {
                    return p.code;
                } else if (p.name) {
                    return p.name;
                }
                return null;
            }).filter(p => p !== null);
        } else {
            this.userPermissions = [];
        }
        
        // 提取角色列表
        if (user.roles && Array.isArray(user.roles)) {
            this.userRoles = user.roles.map(r => {
                if (typeof r === 'string') {
                    return r;
                } else if (r.code) {
                    return r.code;
                } else if (r.name) {
                    return r.name;
                }
                return null;
            }).filter(r => r !== null);
        } else {
            this.userRoles = [];
        }
        
        // 兼容旧的角色字段
        if (user.role) {
            const roleCode = typeof user.role === 'string' ? user.role : (user.role.code || user.role.name);
            if (roleCode && !this.userRoles.includes(roleCode)) {
                this.userRoles.push(roleCode);
            }
        }
        
        if (user.role_code && !this.userRoles.includes(user.role_code)) {
            this.userRoles.push(user.role_code);
        }
    }

    /**
     * 检查是否有权限
     * @param {string|Array<string>} permission - 权限代码或权限代码数组
     * @returns {boolean} 是否有权限
     */
    hasPermission(permission) {
        // 如果是平台管理员，拥有所有权限
        if (this.currentUser && (
            this.currentUser.is_platform_admin ||
            this.currentUser.role === 'platform_admin' ||
            this.currentUser.role_code === 'platform_admin' ||
            this.userRoles.includes('platform_admin')
        )) {
            return true;
        }
        
        // 如果是系统管理员（admin角色），拥有该租户下的所有权限
        if (this.currentUser && (
            this.currentUser.role === 'admin' ||
            this.currentUser.role_code === 'admin' ||
            this.userRoles.includes('admin')
        )) {
            return true;
        }
        
        // 如果没有提供权限要求，返回true（允许访问）
        if (!permission || (Array.isArray(permission) && permission.length === 0)) {
            return true;
        }
        
        // 辅助函数：检查权限是否匹配（支持带租户前缀的权限代码）
        const matchesPermission = (requiredPerm, userPerm) => {
            // 完全匹配
            if (requiredPerm === userPerm) {
                return true;
            }
            // 检查是否带租户前缀（格式：TENANT_CODE_permission:action）
            // 如果用户权限是 TEST001_pharmacy:dispense，而需要的是 pharmacy:dispense，应该匹配
            if (userPerm && userPerm.includes('_')) {
                const parts = userPerm.split('_', 2);
                if (parts.length === 2 && parts[1] === requiredPerm) {
                    return true;
                }
            }
            // 如果需要的权限带前缀，用户权限不带前缀，也应该匹配（向后兼容）
            if (requiredPerm && requiredPerm.includes('_')) {
                const parts = requiredPerm.split('_', 2);
                if (parts.length === 2 && parts[1] === userPerm) {
                    return true;
                }
            }
            return false;
        };
        
        // 如果权限要求是数组，检查是否有任一权限
        if (Array.isArray(permission)) {
            return permission.some(p => 
                this.userPermissions.some(up => matchesPermission(p, up))
            );
        }
        
        // 检查单个权限
        return this.userPermissions.some(up => matchesPermission(permission, up));
    }

    /**
     * 检查是否有角色
     * @param {string|Array<string>} role - 角色代码或角色代码数组
     * @returns {boolean} 是否有角色
     */
    hasRole(role) {
        // 如果是平台管理员，拥有所有角色
        if (this.currentUser && (
            this.currentUser.is_platform_admin ||
            this.currentUser.role === 'platform_admin' ||
            this.currentUser.role_code === 'platform_admin' ||
            this.userRoles.includes('platform_admin')
        )) {
            return true;
        }
        
        if (!role) {
            return false;
        }
        
        if (Array.isArray(role)) {
            return role.some(r => this.userRoles.includes(r));
        }
        
        return this.userRoles.includes(role);
    }
    
    /**
     * 检查是否是系统管理员（租户内的admin角色）
     * @returns {boolean} 是否是系统管理员
     */
    isAdmin() {
        if (!this.currentUser) {
            return false;
        }
        
        // 平台管理员也是管理员
        if (
            this.currentUser.is_platform_admin ||
            this.currentUser.role === 'platform_admin' ||
            this.currentUser.role_code === 'platform_admin' ||
            this.userRoles.includes('platform_admin')
        ) {
            return true;
        }
        
        // 租户内的系统管理员
        return (
            this.currentUser.role === 'admin' ||
            this.currentUser.role_code === 'admin' ||
            this.userRoles.includes('admin')
        );
    }

    /**
     * 检查是否可以访问菜单
     * @param {string} menuRoute - 菜单路由
     * @returns {boolean} 是否可以访问
     */
    canAccessMenu(menuRoute) {
        // 系统管理员（admin）可以访问所有菜单
        if (this.isAdmin()) {
            console.log(`[MENU-DEBUG] canAccessMenu(${menuRoute}) => true (isAdmin)`);
            return true;
        }
        
        const requiredPermissions = MENU_PERMISSIONS[menuRoute];
        if (!requiredPermissions || (Array.isArray(requiredPermissions) && requiredPermissions.length === 0)) {
            // 如果菜单没有定义权限要求（如工作台），默认允许访问
            console.log(`[MENU-DEBUG] canAccessMenu(${menuRoute}) => true (无权限要求)`);
            return true;
        }
        
        // 1) 精确 / 带租户前缀匹配（兼容 TEST001_treatment:list 等历史码）
        if (this.hasPermission(requiredPermissions)) {
            console.log(`[MENU-DEBUG] canAccessMenu(${menuRoute}) => true (精确匹配 ${JSON.stringify(requiredPermissions)})`);
            return true;
        }
        
        // 2) 资源级兜底：用户对该资源拥有任意权限即可见菜单。
        //    兼容动作码差异（view/list/get/create/update/delete）与历史前缀，
        //    避免“权限码对齐未完成时菜单整片空白”的问题。
        const firstPerm = Array.isArray(requiredPermissions) ? requiredPermissions[0] : requiredPermissions;
        const normFirst = (typeof firstPerm === 'string' && firstPerm.includes('_'))
            ? firstPerm.split('_', 2)[1]
            : firstPerm;
        const resource = (typeof normFirst === 'string' && normFirst.includes(':'))
            ? normFirst.split(':', 2)[0]
            : normFirst;
        if (this.hasResourcePermission(resource)) {
            console.log(`[MENU-DEBUG] canAccessMenu(${menuRoute}) => true (资源兜底 resource=${resource})`);
            return true;
        }
        
        console.log(`[MENU-DEBUG] canAccessMenu(${menuRoute}) => false (要求 ${JSON.stringify(requiredPermissions)}，用户无匹配；userPermissions=${JSON.stringify(this.userPermissions)})`);
        return false;
    }

    /**
     * 检查是否拥有某资源的任意权限（兼容动作码差异与历史租户前缀）
     * 例：用户拥有 TEST001_treatment:view 或 treatment:create，均视为“拥有 treatment 资源的权限”
     * @param {string} resource - 资源代码，如 treatment / patient / pharmacy
     * @returns {boolean}
     */
    hasResourcePermission(resource) {
        if (!resource || this.isAdmin()) {
            return true;
        }
        const target = resource + ':';
        return this.userPermissions.some(up => {
            // 兼容历史前缀 TENANT_resource:action
            const norm = (typeof up === 'string' && up.includes('_')) ? up.split('_', 2)[1] : up;
            return norm === resource || (typeof norm === 'string' && norm.startsWith(target));
        });
    }

    /**
     * 检查是否可以执行功能
     * @param {string} functionCode - 功能代码
     * @returns {boolean} 是否可以执行
     */
    canExecuteFunction(functionCode) {
        // 系统管理员（admin）可以执行所有功能
        if (this.isAdmin()) {
            return true;
        }
        
        const requiredPermissions = FUNCTION_PERMISSIONS[functionCode];
        if (!requiredPermissions) {
            // 如果功能没有定义权限要求，默认允许执行
            return true;
        }
        return this.hasPermission(requiredPermissions);
    }

    /**
     * 获取用户权限列表
     * @returns {Array<string>} 权限列表
     */
    getPermissions() {
        return [...this.userPermissions];
    }

    /**
     * 获取用户角色列表
     * @returns {Array<string>} 角色列表
     */
    getRoles() {
        return [...this.userRoles];
    }
}

// 创建全局权限管理器实例
const permissionManager = new PermissionManager();

// 全局权限检查函数（兼容旧代码）
window.hasPermission = function(permission) {
    return permissionManager.hasPermission(permission);
};

// 全局角色检查函数
window.hasRole = function(role) {
    return permissionManager.hasRole(role);
};

// 全局菜单访问检查函数
window.canAccessMenu = function(menuRoute) {
    return permissionManager.canAccessMenu(menuRoute);
};

// 全局功能执行检查函数
window.canExecuteFunction = function(functionCode) {
    return permissionManager.canExecuteFunction(functionCode);
};

// 全局系统管理员检查函数
window.isAdmin = function() {
    return permissionManager.isAdmin();
};

// 导出权限管理器
window.PermissionManager = PermissionManager;
window.permissionManager = permissionManager;

