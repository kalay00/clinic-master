/**
 * API调用封装
 * 提供各个业务模块的API调用方法
 */

// API客户端类（如果app.js未加载，则在此定义）
if (typeof ApiClient === 'undefined') {
    window.ApiClient = class ApiClient {
        constructor() {
            this.baseURL = '/api/v1';
            this.tokenKey = 'his_token';
        }

        async request(url, options = {}) {
            const token = localStorage.getItem(this.tokenKey);
            
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
                const response = await fetch(`${this.baseURL}${url}`, config);
                
                if (!response.ok) {
                    let errorData;
                    try {
                        errorData = await response.json();
                    } catch {
                        errorData = { message: `HTTP error! status: ${response.status}` };
                    }
                    
                    const error = new Error(errorData.message || `HTTP error! status: ${response.status}`);
                    error.response = { data: errorData, status: response.status };
                    throw error;
                }

                const data = await response.json();
                
                if (data.code !== 200) {
                    const error = new Error(data.message || '请求失败');
                    error.code = data.code;
                    error.data = data.data;
                    error.response = { data: data, status: response.status };
                    
                    if (data.code === 401 || response.status === 401) {
                        localStorage.removeItem(this.tokenKey);
                        localStorage.removeItem('his_user');
                        if (!window.location.pathname.includes('login')) {
                            setTimeout(() => {
                                window.location.href = '/login.html';
                            }, 2000);
                        }
                    }
                    
                    throw error;
                }
                
                return data.data || data;
            } catch (error) {
                console.error('API请求失败:', error);
                throw error;
            }
        }

        get(url, params = {}) {
            const cleanParams = {};
            Object.keys(params).forEach(key => {
                if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
                    cleanParams[key] = params[key];
                }
            });
            
            const queryString = new URLSearchParams(cleanParams).toString();
            const fullUrl = queryString ? `${url}?${queryString}` : url;
            
            return this.request(fullUrl, { method: 'GET' });
        }

        post(url, data = null, params = {}) {
            const cleanParams = {};
            Object.keys(params).forEach(key => {
                if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
                    cleanParams[key] = params[key];
                }
            });
            
            const queryString = new URLSearchParams(cleanParams).toString();
            const fullUrl = queryString ? `${url}?${queryString}` : url;
            
            return this.request(fullUrl, {
                method: 'POST',
                body: data ? (data instanceof FormData ? data : JSON.stringify(data)) : null
            });
        }

        put(url, data = null, params = {}) {
            const cleanParams = {};
            Object.keys(params).forEach(key => {
                if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
                    cleanParams[key] = params[key];
                }
            });
            
            const queryString = new URLSearchParams(cleanParams).toString();
            const fullUrl = queryString ? `${url}?${queryString}` : url;
            
            return this.request(fullUrl, {
                method: 'PUT',
                body: data ? (data instanceof FormData ? data : JSON.stringify(data)) : null
            });
        }

        delete(url, params = {}) {
            const cleanParams = {};
            Object.keys(params).forEach(key => {
                if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
                    cleanParams[key] = params[key];
                }
            });
            
            const queryString = new URLSearchParams(cleanParams).toString();
            const fullUrl = queryString ? `${url}?${queryString}` : url;
            
            return this.request(fullUrl, { method: 'DELETE' });
        }
    };
}

// 确保 ApiClient 在全局作用域可用
const ApiClientClass = window.ApiClient || (typeof ApiClient !== 'undefined' ? ApiClient : null);

// 创建API客户端实例（如果window.api不存在）
if (typeof window.api === 'undefined') {
    if (ApiClientClass) {
        window.api = new ApiClientClass();
    } else {
        console.error('ApiClient 类未定义，无法创建 API 客户端');
    }
}

// 创建一个本地引用，避免重复声明const api
// 如果window.api已存在（由app.js创建），直接使用；否则创建新的
if (typeof window.api === 'undefined' && ApiClientClass) {
    window.api = new ApiClientClass();
}

// 创建本地引用（不声明const api，避免与app.js冲突）
// 所有API方法都使用window.api
// 使用一个辅助函数来获取api实例
const getApi = () => {
    if (!window.api) {
        console.error('API客户端未初始化');
    }
    return window.api;
};

/**
 * 认证API
 */
const AuthAPI = {
    /**
     * 用户登录
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise} 登录结果
     */
    async login(username, password) {
        return await getApi().post('/auth/login', { username, password });
    },

    /**
     * 用户登出
     */
    async logout() {
        return await getApi().post('/auth/logout');
    },

    /**
     * 刷新Token
     */
    async refreshToken() {
        return await getApi().post('/auth/refresh');
    }
};

/**
 * 患者API
 */
const PatientAPI = {
    /**
     * 获取患者列表
     * @param {object} params - 查询参数 {skip, limit, search}
     * @returns {Promise} 患者列表 {items: [], pagination: {total, page, page_size, pages}}
     */
    async getList(params = {}) {
        // 转换前端参数为后端参数
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10,
            search: params.keyword || params.search || ''
        };
        return await getApi().get('/patients', backendParams);
    },

    /**
     * 获取患者详情
     * @param {string} id - 患者ID
     * @returns {Promise} 患者详情
     */
    async getDetail(id) {
        return await getApi().get(`/patients/${id}`);
    },

    /**
     * 创建患者
     * @param {object} data - 患者数据
     * @returns {Promise} 创建结果
     */
    async create(data) {
        return await getApi().post('/patients', data);
    },

    /**
     * 更新患者
     * @param {string} id - 患者ID
     * @param {object} data - 患者数据
     * @returns {Promise} 更新结果
     */
    async update(id, data) {
        return await getApi().put(`/patients/${id}`, data);
    },

    /**
     * 删除患者
     * @param {string} id - 患者ID
     * @returns {Promise} 删除结果
     */
    async delete(id) {
        return await getApi().delete(`/patients/${id}`);
    },

    /**
     * 搜索患者
     * @param {string} keyword - 搜索关键词
     * @returns {Promise} 搜索结果 {items: []}
     */
    async search(keyword) {
        const result = await getApi().get('/patients', { search: keyword, limit: 50 });
        return result.items || [];
    },

    /**
     * 获取就诊历史
     * @param {string} id - 患者ID
     * @returns {Promise} 就诊历史
     */
    async getVisits(id) {
        return await getApi().get(`/patients/${id}/visits`);
    }
};

/**
 * 挂号API
 */
const RegistrationAPI = {
    /**
     * 获取挂号列表
     * @param {object} params - 查询参数 {page, page_size, keyword, status}
     * @returns {Promise} 挂号列表 {items: [], pagination: {}}
     */
    async getList(params = {}) {
        // 转换前端参数为后端参数
        const backendParams = {
            skip: ((params.page || 1) - 1) * (params.page_size || 10),
            limit: params.page_size || 10
        };
        if (params.keyword || params.search) {
            // 后端暂不支持keyword搜索，可以通过patient_id等筛选
            // 这里先不传keyword，后续可以扩展
        }
        if (params.status) {
            backendParams.status = params.status;
        }
        if (params.patient_id) {
            backendParams.patient_id = params.patient_id;
        }
        if (params.payment_status) {
            backendParams.payment_status = params.payment_status;
        }
        return await getApi().get('/registrations', backendParams);
    },
    
    /**
     * 获取挂号详情
     * @param {string} id - 挂号ID
     * @returns {Promise} 挂号详情
     */
    async getDetail(id) {
        return await getApi().get(`/registrations/${id}`);
    },

    /**
     * 创建挂号
     * @param {object} data - 挂号数据
     * @returns {Promise} 创建结果
     */
    async create(data) {
        return await getApi().post('/registrations', data);
    },

    /**
     * 取消挂号
     * @param {string} id - 挂号ID
     * @returns {Promise} 取消结果
     */
    async cancel(id) {
        return await getApi().post(`/registrations/${id}/cancel`);
    },

    /**
     * 支付挂号费
     * @param {string} id - 挂号ID
     * @param {object} data - 支付数据 {payment_method, amount, transaction_id}
     * @returns {Promise} 支付结果
     */
    async payFee(id, data) {
        return await getApi().post(`/registrations/${id}/pay`, data);
    },

    /**
     * 退挂号费
     * @param {string} id - 挂号ID
     * @param {object} data - 退费数据 {refund_amount, reason}
     * @returns {Promise} 退费结果
     */
    async refundFee(id, data) {
        return await getApi().post(`/registrations/${id}/refund`, data);
    },

    /**
     * 获取排班列表
     * @param {object} params - 查询参数 {page, page_size, doctor_id, department_id, date, start_date, end_date}
     * @returns {Promise} 排班列表 {items: [], pagination: {}}
     */
    async getSchedules(params = {}) {
        // 转换前端参数为后端参数
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10
        };
        if (params.doctor_id) backendParams.doctor_id = params.doctor_id;
        if (params.department_id) backendParams.department_id = params.department_id;
        if (params.date) backendParams.schedule_date = params.date;  // 后端使用schedule_date参数名
        if (params.start_date) backendParams.start_date = params.start_date;
        if (params.end_date) backendParams.end_date = params.end_date;
        return await getApi().get('/registrations/schedules', backendParams);
    },

    /**
     * 创建排班
     * @param {object} data - 排班数据
     * @returns {Promise} 创建结果
     */
    async createSchedule(data) {
        return await getApi().post('/registrations/schedules', data);
    },

    /**
     * 获取排班详情
     * @param {string} id - 排班ID
     * @returns {Promise} 排班详情
     */
    async getScheduleDetail(id) {
        return await getApi().get(`/registrations/schedules/${id}`);
    },

    /**
     * 更新排班
     * @param {string} id - 排班ID
     * @param {object} data - 排班数据
     * @returns {Promise} 更新结果
     */
    async updateSchedule(id, data) {
        return await getApi().put(`/registrations/schedules/${id}`, data);
    },

    /**
     * 删除排班
     * @param {string} id - 排班ID
     * @returns {Promise} 删除结果
     */
    async deleteSchedule(id) {
        return await getApi().delete(`/registrations/schedules/${id}`);
    },

    /**
     * 暂停挂号
     * @param {string} id - 排班ID
     * @returns {Promise} 暂停结果
     */
    async pauseSchedule(id) {
        return await getApi().post(`/registrations/schedules/${id}/pause`);
    },

    /**
     * 恢复挂号
     * @param {string} id - 排班ID
     * @returns {Promise} 恢复结果
     */
    async resumeSchedule(id) {
        return await getApi().post(`/registrations/schedules/${id}/resume`);
    },

    /**
     * 换班
     * @param {string} id - 排班ID
     * @param {string} newDoctorId - 新医生ID
     * @returns {Promise} 换班结果
     */
    async swapSchedule(id, newDoctorId) {
        return await getApi().post(`/registrations/schedules/${id}/swap?new_doctor_id=${encodeURIComponent(newDoctorId)}`);
    }
};

/**
 * 诊疗API
 */
const TreatmentAPI = {
    /**
     * 获取病历列表
     * @param {object} params - 查询参数 {page, page_size, keyword}
     * @returns {Promise} 病历列表 {items: [], pagination: {}}
     */
    async getMedicalRecords(params = {}) {
        // 转换前端参数为后端参数
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10,
            search: params.keyword || params.search || ''
        };
        if (params.patient_id) {
            backendParams.patient_id = params.patient_id;
        }
        if (params.doctor_id) {
            backendParams.doctor_id = params.doctor_id;
        }
        if (params.registration_id) {
            backendParams.registration_id = params.registration_id;
        }
        if (params.start_date) {
            backendParams.start_date = params.start_date;
        }
        if (params.end_date) {
            backendParams.end_date = params.end_date;
        }
        return await getApi().get('/treatments', backendParams);
    },
    
    /**
     * 获取病历列表（别名，兼容getList调用）
     * @param {object} params - 查询参数 {page, page_size, keyword, patient_id}
     * @returns {Promise} 病历列表 {items: [], pagination: {}}
     */
    async getList(params = {}) {
        return await this.getMedicalRecords(params);
    },

    /**
     * 创建病历
     * @param {object} data - 病历数据
     * @returns {Promise} 创建结果
     */
    async createMedicalRecord(data) {
        return await getApi().post('/treatments', data);
    },

    /**
     * 获取处方列表
     * @param {object} params - 查询参数 {page, page_size, keyword}
     * @returns {Promise} 处方列表 {items: [], pagination: {}}
     */
    async getPrescriptions(params = {}) {
        // 转换前端参数为后端参数
        const backendParams = {
            skip: ((params.page || 1) - 1) * (params.page_size || 10),
            limit: params.page_size || 10
        };
        
        // 添加可选的筛选参数
        if (params.patient_id) {
            backendParams.patient_id = params.patient_id;
        }
        if (params.doctor_id) {
            backendParams.doctor_id = params.doctor_id;
        }
        if (params.medical_record_id) {
            backendParams.medical_record_id = params.medical_record_id;
        }
        if (params.status) {
            backendParams.status = params.status;
        }
        return await getApi().get('/treatments/prescriptions', backendParams);
    },
    
    /**
     * 获取最近就诊记录
     * @param {object} params - 查询参数 {limit}
     * @returns {Promise} 就诊记录列表
     */
    async getRecentVisits(params = {}) {
        return await this.getMedicalRecords({ page: 1, page_size: params.limit || 10 });
    },

    /**
     * 创建处方
     * @param {object} data - 处方数据
     * @returns {Promise} 创建结果
     */
    async createPrescription(data) {
        return await getApi().post('/treatments/prescriptions', data);
    },
    
    /**
     * 获取处方详情
     * @param {string} id - 处方ID
     * @returns {Promise} 处方详情
     */
    async getPrescriptionDetail(id) {
        return await getApi().get(`/treatments/prescriptions/${id}`);
    },
    
    /**
     * 更新处方
     * @param {string} id - 处方ID
     * @param {object} data - 处方数据
     * @returns {Promise} 更新结果
     */
    async updatePrescription(id, data) {
        return await getApi().put(`/treatments/prescriptions/${id}`, data);
    },
    
    /**
     * 删除处方
     * @param {string} id - 处方ID
     * @returns {Promise} 删除结果
     */
    async deletePrescription(id) {
        return await getApi().delete(`/treatments/prescriptions/${id}`);
    },
    
    /**
     * 获取病历详情
     * @param {string} id - 病历ID
     * @returns {Promise} 病历详情
     */
    async getMedicalRecordDetail(id) {
        return await getApi().get(`/treatments/${id}`);
    },
    
    /**
     * 更新病历
     * @param {string} id - 病历ID
     * @param {object} data - 病历数据
     * @returns {Promise} 更新结果
     */
    async updateMedicalRecord(id, data) {
        return await getApi().put(`/treatments/${id}`, data);
    }
};

/**
 * 收费API
 */
const PaymentAPI = {
    /**
     * 获取账单列表
     * @param {object} params - 查询参数 {page, page_size, keyword}
     * @returns {Promise} 账单列表 {items: [], pagination: {}}
     */
    async getBills(params = {}) {
        // 转换前端参数为后端参数
        const backendParams = {
            skip: ((params.page || 1) - 1) * (params.page_size || 10),
            limit: params.page_size || 10
        };
        if (params.registration_id) {
            backendParams.registration_id = params.registration_id;
        }
        if (params.status) {
            backendParams.status = params.status;
        }
        if (params.bill_type) {
            backendParams.bill_type = params.bill_type;
        }
        if (params.patient_id) {
            backendParams.patient_id = params.patient_id;
        }
        return await getApi().get('/payments/bills', backendParams);
    },

    /**
     * 创建账单
     * @param {object} data - 账单数据
     * @returns {Promise} 创建结果
     */
    async createBill(data) {
        return await getApi().post('/payments/bills', data);
    },

    /**
     * 支付账单
     * @param {string} id - 账单ID
     * @param {object} data - 支付数据
     * @returns {Promise} 支付结果
     */
    async payBill(id, data) {
        return await getApi().post(`/payments/bills/${id}/pay`, data);
    },

    /**
     * 退费
     * @param {string} id - 账单ID
     * @param {object} data - 退费数据
     * @returns {Promise} 退费结果
     */
    async refund(id, data) {
        return await getApi().post(`/payments/bills/${id}/refund`, data);
    },
    
    /**
     * 获取账单详情
     * @param {string} id - 账单ID
     * @returns {Promise} 账单详情
     */
    async getBillDetail(id) {
        return await getApi().get(`/payments/bills/${id}`);
    },

    /**
     * 获取支付记录列表
     * @param {object} params - 查询参数
     * @returns {Promise} 支付记录列表
     */
    async getPayments(params = {}) {
        return await getApi().get('/payments/payments', params);
    }
};

/**
 * 药房API
 */
const PharmacyAPI = {
    /**
     * 获取药品列表
     * @param {object} params - 查询参数 {page, page_size, keyword, type}
     * @returns {Promise} 药品列表 {items: [], pagination: {}}
     */
    async getDrugs(params = {}) {
        // 转换前端参数为后端参数
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10,
            search: params.keyword || params.search || ''
        };
        if (params.category) backendParams.category = params.category;
        return await getApi().get('/pharmacy/drugs', backendParams);
    },

    /**
     * 创建药品
     * @param {object} data - 药品数据
     * @returns {Promise} 创建结果
     */
    async createDrug(data) {
        return await getApi().post('/pharmacy/drugs', data);
    },

    /**
     * 获取药品详情
     * @param {string} id - 药品ID
     * @returns {Promise} 药品详情
     */
    async getDrug(id) {
        return await getApi().get(`/pharmacy/drugs/${id}`);
    },

    /**
     * 更新药品
     * @param {string} id - 药品ID
     * @param {object} data - 药品数据
     * @returns {Promise} 更新结果
     */
    async updateDrug(id, data) {
        return await getApi().put(`/pharmacy/drugs/${id}`, data);
    },

    /**
     * 获取库存列表
     * @param {object} params - 查询参数 {page, page_size, keyword}
     * @returns {Promise} 库存列表 {items: [], pagination: {}}
     */
    async getInventory(params = {}) {
        // 转换前端参数为后端参数
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10,
            search: params.keyword || params.search || ''
        };
        return await getApi().get('/pharmacy/inventory', backendParams);
    },
    
    /**
     * 获取库存预警
     * @returns {Promise} 预警数据 {low_stock: [], expired: [], expiring_soon: []}
     */
    async getInventoryWarnings() {
        return await getApi().get('/pharmacy/inventory/warnings');
    },
    
    /**
     * 入库
     * @param {object} data - 入库数据
     * @returns {Promise} 入库结果
     */
    async stockIn(data) {
        return await getApi().post('/pharmacy/inventory/in', data);
    },
    
    /**
     * 出库
     * @param {object} data - 出库数据
     * @returns {Promise} 出库结果
     */
    async stockOut(data) {
        return await getApi().post('/pharmacy/inventory/out', data);
    },

    /**
     * 发药
     * @param {string} prescriptionId - 处方ID
     * @returns {Promise} 发药结果
     */
    async dispensePrescription(prescriptionId, items = null) {
        // 后端API路径是 /pharmacy/drugs/dispense（pharmacy 路由挂载前缀为 /pharmacy/drugs），
        // 需要在请求体中传递 prescription_id 和 items
        // 如果未提供items，需要先从处方中获取
        let requestBody = {
            prescription_id: prescriptionId
        };
        
        if (items && Array.isArray(items) && items.length > 0) {
            // 如果提供了发药明细，直接使用
            requestBody.items = items;
        } else {
            // 如果没有提供items，需要先获取处方详情，然后提取items
            try {
                // 使用 TreatmentAPI 获取处方详情
                const prescriptionResponse = await window.TreatmentAPI.getPrescriptionDetail(prescriptionId);
                const prescription = prescriptionResponse.data || prescriptionResponse;
                
                if (prescription && prescription.items) {
                    // 将处方的items转换为发药所需的格式
                    const dispenseItems = [];
                    if (typeof prescription.items === 'object' && !Array.isArray(prescription.items)) {
                        // items是对象，转换为数组
                        for (const [drugId, item] of Object.entries(prescription.items)) {
                            if (item && typeof item === 'object') {
                                dispenseItems.push({
                                    drug_id: drugId,
                                    quantity: item.quantity || item.amount || 1
                                });
                            }
                        }
                    } else if (Array.isArray(prescription.items)) {
                        // items是数组
                        for (const item of prescription.items) {
                            dispenseItems.push({
                                drug_id: item.drug_id || item.id,
                                quantity: item.quantity || item.amount || 1
                            });
                        }
                    }
                    requestBody.items = dispenseItems;
                } else {
                    throw new Error('处方中没有药品明细');
                }
            } catch (error) {
                console.error('获取处方详情失败:', error);
                throw new Error('无法获取处方详情，请手动指定发药明细');
            }
        }
        
        return await getApi().post('/pharmacy/drugs/dispense', requestBody);
    }
};

/**
 * 报表API
 */
const ReportAPI = {
    /**
     * 获取收入报表
     * @param {object} params - 查询参数 {start_date, end_date}
     * @returns {Promise} 收入报表数据
     */
    async getRevenueReport(params = {}) {
        return await getApi().get('/reports/revenue', params);
    },
    
    /**
     * 获取工作台统计数据
     * @param {object} params - 查询参数 {target_date}
     * @returns {Promise} 统计数据
     */
    async getDashboardStats(params = {}) {
        return await getApi().get('/reports/dashboard', params);
    },

    /**
     * 获取就诊量报表
     * @param {object} params - 查询参数
     * @returns {Promise} 就诊量报表
     */
    async getVisitsReport(params = {}) {
        return await getApi().get('/reports/visits', params);
    },

    /**
     * 获取药品销售报表
     * @param {object} params - 查询参数
     * @returns {Promise} 药品销售报表
     */
    async getDrugsReport(params = {}) {
        return await getApi().get('/reports/drugs', params);
    },

    /**
     * 获取每日统计
     * @param {object} params - 查询参数（target_date可选）
     * @returns {Promise} 每日统计数据
     */
    async getDailyStatistics(params = {}) {
        return await getApi().get('/reports/daily', params);
    },
    
    /**
     * 获取患者统计报表
     * @param {object} params - 查询参数 {start_date, end_date}
     * @returns {Promise} 患者统计报表数据
     */
    async getPatientsReport(params = {}) {
        return await getApi().get('/reports/patients', params);
    }
};

/**
 * 通知API
 */
const NotificationAPI = {
    /**
     * 发送短信通知
     * @param {object} data - 通知数据（phone, message）
     * @returns {Promise} 发送结果
     */
    async sendSMS(data) {
        return await getApi().post('/notifications/sms', data);
    },

    /**
     * 发送微信通知
     * @param {object} data - 通知数据（openid, template_id, data）
     * @returns {Promise} 发送结果
     */
    async sendWeChat(data) {
        return await getApi().post('/notifications/wechat', data);
    }
};

/**
 * 用户管理API
 */
const UserAPI = {
    /**
     * 获取用户列表
     * @param {object} params - 查询参数 {page, page_size, keyword}
     * @returns {Promise} 用户列表 {items: [], pagination: {}}
     */
    async getList(params = {}) {
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10,
            search: params.keyword || params.search || ''
        };
        return await getApi().get('/users', backendParams);
    },
    
    /**
     * 获取用户详情
     * @param {string} id - 用户ID
     * @returns {Promise} 用户详情
     */
    async getDetail(id) {
        return await getApi().get(`/users/${id}`);
    },
    
    /**
     * 创建用户
     * @param {object} data - 用户数据
     * @returns {Promise} 创建结果
     */
    async create(data) {
        return await getApi().post('/users', data);
    },
    
    /**
     * 更新用户
     * @param {string} id - 用户ID
     * @param {object} data - 用户数据
     * @returns {Promise} 更新结果
     */
    async update(id, data) {
        return await getApi().put(`/users/${id}`, data);
    },
    
    /**
     * 删除用户
     * @param {string} id - 用户ID
     * @returns {Promise} 删除结果
     */
    async delete(id) {
        return await getApi().delete(`/users/${id}`);
    },
    
    /**
     * 为用户分配角色
     * @param {string} userId - 用户ID
     * @param {string} roleId - 角色ID
     * @returns {Promise} 分配结果
     */
    async assignRole(userId, roleId) {
        return await getApi().post(`/users/${userId}/roles`, { role_id: roleId });
    },
    
    /**
     * 获取当前用户信息
     * @returns {Promise} 当前用户信息
     */
    async getCurrentUserInfo() {
        return await getApi().get('/auth/me');
    },
    
    /**
     * 更新当前用户信息
     * @param {object} data - 更新数据 {real_name, phone, email, password}
     * @returns {Promise} 更新结果
     */
    async updateCurrentUser(data) {
        return await getApi().put('/auth/me', data);
    }
};

/**
 * 角色管理API
 */
const RoleAPI = {
    /**
     * 获取角色列表
     * @returns {Promise} 角色列表
     */
    async getList() {
        return await getApi().get('/roles');
    },
    
    /**
     * 获取角色详情
     * @param {string} id - 角色ID
     * @returns {Promise} 角色详情
     */
    async getDetail(id) {
        return await getApi().get(`/roles/${id}`);
    },
    
    /**
     * 创建角色
     * @param {object} data - 角色数据
     * @returns {Promise} 创建结果
     */
    async create(data) {
        return await getApi().post('/roles', data);
    },
    
    /**
     * 更新角色
     * @param {string} id - 角色ID
     * @param {object} data - 角色数据
     * @returns {Promise} 更新结果
     */
    async update(id, data) {
        return await getApi().put(`/roles/${id}`, data);
    },
    
    /**
     * 删除角色
     * @param {string} id - 角色ID
     * @returns {Promise} 删除结果
     */
    async delete(id) {
        return await getApi().delete(`/roles/${id}`);
    },
    
    /**
     * 分配权限
     * @param {string} id - 角色ID
     * @param {Array<string>} permissionIds - 权限ID列表
     * @returns {Promise} 分配结果
     */
    async assignPermissions(id, permissionIds) {
        return await getApi().post(`/roles/${id}/permissions`, { permission_ids: permissionIds });
    },
    
    /**
     * 获取所有权限
     * @returns {Promise} 权限列表
     */
    async getAllPermissions() {
        return await getApi().get('/roles/permissions/all');
    }
};

/**
 * 科室管理API
 */
const DepartmentAPI = {
    /**
     * 获取科室列表
     * @param {object} params - 查询参数 {page, page_size, keyword}
     * @returns {Promise} 科室列表 {items: [], pagination: {}}
     */
    async getList(params = {}) {
        const backendParams = {
            skip: ((params.page || 1) - 1) * (params.page_size || 100),
            limit: params.page_size || 100,
            search: params.keyword || params.search || ''
        };
        return await getApi().get('/departments', backendParams);
    },
    
    /**
     * 获取科室详情
     * @param {string} id - 科室ID
     * @returns {Promise} 科室详情
     */
    async getDetail(id) {
        return await getApi().get(`/departments/${id}`);
    },
    
    /**
     * 创建科室
     * @param {object} data - 科室数据
     * @returns {Promise} 创建结果
     */
    async create(data) {
        return await getApi().post('/departments', data);
    },
    
    /**
     * 更新科室
     * @param {string} id - 科室ID
     * @param {object} data - 科室数据
     * @returns {Promise} 更新结果
     */
    async update(id, data) {
        return await getApi().put(`/departments/${id}`, data);
    },
    
    /**
     * 删除科室
     * @param {string} id - 科室ID
     * @returns {Promise} 删除结果
     */
    async delete(id) {
        return await getApi().delete(`/departments/${id}`);
    }
};

/**
 * 医生管理API
 */
const DoctorAPI = {
    /**
     * 获取医生列表
     * @param {object} params - 查询参数 {page, page_size, keyword, department_id}
     * @returns {Promise} 医生列表 {items: [], pagination: {}}
     */
    async getList(params = {}) {
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10,
            search: params.keyword || params.search || ''
        };
        if (params.department_id) backendParams.department_id = params.department_id;
        return await getApi().get('/doctors', backendParams);
    },
    
    /**
     * 获取医生详情
     * @param {string} id - 医生ID
     * @returns {Promise} 医生详情
     */
    async getDetail(id) {
        return await getApi().get(`/doctors/${id}`);
    },
    
    /**
     * 创建医生
     * @param {object} data - 医生数据
     * @returns {Promise} 创建结果
     */
    async create(data) {
        return await getApi().post('/doctors', data);
    },
    
    /**
     * 更新医生
     * @param {string} id - 医生ID
     * @param {object} data - 医生数据
     * @returns {Promise} 更新结果
     */
    async update(id, data) {
        return await getApi().put(`/doctors/${id}`, data);
    },
    
    /**
     * 删除医生
     * @param {string} id - 医生ID
     * @returns {Promise} 删除结果
     */
    async delete(id) {
        return await getApi().delete(`/doctors/${id}`);
    }
};

/**
 * 文件上传API
 */
const UploadAPI = {
    /**
     * 上传图片
     * @param {File} file - 图片文件
     * @returns {Promise} 上传结果 {url, filename}
     */
    async uploadImage(file) {
        const formData = new FormData();
        formData.append('file', file);
        // 注意：使用FormData时，不要手动设置Content-Type，让浏览器自动设置（包括boundary）
        return await getApi().post('/upload/image', formData);
    },
    
    /**
     * 删除图片
     * @param {string} url - 图片URL
     * @returns {Promise} 删除结果
     */
    async deleteImage(url) {
        return await getApi().delete(`/upload/image?url=${encodeURIComponent(url)}`);
    }
};

/**
 * 对接服务API
 */
const IntegrationAPI = {
    /**
     * 医保验证
     * @param {object} data - 验证数据（patient_id, id_card）
     * @returns {Promise} 验证结果
     */
    async verifyMedicalInsurance(data) {
        return await getApi().post('/integrations/medical-insurance/verify', data);
    },

    /**
     * 医保支付
     * @param {object} data - 支付数据（bill_id, amount）
     * @returns {Promise} 支付结果
     */
    async payMedicalInsurance(data) {
        return await getApi().post('/integrations/medical-insurance/pay', data);
    },

    /**
     * 微信支付
     * @param {object} data - 支付数据（bill_id, amount, openid）
     * @returns {Promise} 支付结果
     */
    async payWeChat(data) {
        return await getApi().post('/integrations/wechat/pay', data);
    },

    /**
     * 支付宝支付
     * @param {object} data - 支付数据（bill_id, amount）
     * @returns {Promise} 支付结果
     */
    async payAlipay(data) {
        return await getApi().post('/integrations/alipay/pay', data);
    },

    /**
     * 微信授权
     * @param {object} data - 授权数据（code）
     * @returns {Promise} 授权结果
     */
    async authWeChat(data) {
        return await getApi().post('/integrations/wechat/auth', data);
    }
};

/**
 * 第三方服务配置API
 */
const ThirdPartyConfigAPI = {
    /**
     * 获取所有配置列表
     * @returns {Promise} 配置列表 {items: []}
     */
    async getList() {
        return await getApi().get('/third-party/configs');
    },

    /**
     * 获取指定服务配置
     * @param {string} serviceType - 服务类型（aliyun_sms, alipay, wechat_pay, unionpay）
     * @returns {Promise} 配置信息
     */
    async getConfig(serviceType) {
        return await getApi().get(`/third-party/configs/${serviceType}`);
    },

    /**
     * 保存配置
     * @param {object} data - 配置数据 {service_type, config_data, is_enabled}
     * @returns {Promise} 保存结果
     */
    async saveConfig(data) {
        return await getApi().post('/third-party/configs', data);
    },

    /**
     * 更新配置
     * @param {string} serviceType - 服务类型
     * @param {object} data - 配置数据
     * @returns {Promise} 更新结果
     */
    async updateConfig(serviceType, data) {
        return await getApi().put(`/third-party/configs/${serviceType}`, data);
    },

    /**
     * 删除配置
     * @param {string} serviceType - 服务类型
     * @returns {Promise} 删除结果
     */
    async deleteConfig(serviceType) {
        return await getApi().delete(`/third-party/configs/${serviceType}`);
    },

    /**
     * 测试配置
     * @param {string} serviceType - 服务类型
     * @param {object} testParams - 测试参数
     * @returns {Promise} 测试结果
     */
    async testConfig(serviceType, testParams = {}) {
        return await getApi().post(`/third-party/configs/${serviceType}/test`, {
            test_params: testParams
        });
    }
};

// 导出API对象
window.AuthAPI = AuthAPI;
window.PatientAPI = PatientAPI;
window.RegistrationAPI = RegistrationAPI;
window.TreatmentAPI = TreatmentAPI;
window.PaymentAPI = PaymentAPI;
window.PharmacyAPI = PharmacyAPI;
window.ReportAPI = ReportAPI;
/**
 * 租户配置API
 */
const TenantAPI = {
    /**
     * 获取租户配置
     * @returns {Promise} 租户配置
     */
    async getConfig() {
        return await getApi().get('/tenant/config');
    },
    
    /**
     * 更新租户配置
     * @param {object} data - 配置数据 {config: {...}}
     * @returns {Promise} 更新结果
     */
    async updateConfig(data) {
        return await getApi().put('/tenant/config', data);
    },
    
    /**
     * 获取药师审核状态
     * @returns {Promise} 审核状态
     */
    async getPharmacistReviewStatus() {
        return await getApi().get('/tenant/pharmacist-review-status');
    }
};

window.NotificationAPI = NotificationAPI;
window.IntegrationAPI = IntegrationAPI;
window.UserAPI = UserAPI;
window.RoleAPI = RoleAPI;
window.DepartmentAPI = DepartmentAPI;
window.DoctorAPI = DoctorAPI;
window.UploadAPI = UploadAPI;
window.ThirdPartyConfigAPI = ThirdPartyConfigAPI;
window.TenantAPI = TenantAPI;

/**
 * 平台管理API
 */
const PlatformAPI = {
    /**
     * 平台管理员登录
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise} 登录结果
     */
    async login(username, password) {
        return await getApi().post('/platform/login', { username, password });
    },

    /**
     * 获取所有租户列表
     * @param {object} params - 查询参数 {search, status, skip, limit}
     * @returns {Promise} 租户列表 {items: [], pagination: {}}
     */
    async getTenants(params = {}) {
        const backendParams = {
            skip: params.skip || (params.page - 1) * (params.page_size || 10) || 0,
            limit: params.limit || params.page_size || 100
        };
        if (params.search) backendParams.search = params.search;
        if (params.status) backendParams.status = params.status;
        return await getApi().get('/platform/tenants', backendParams);
    },

    /**
     * 获取租户详情
     * @param {string} id - 租户ID
     * @returns {Promise} 租户详情
     */
    async getTenantDetail(id) {
        return await getApi().get(`/platform/tenants/${id}`);
    },

    /**
     * 创建租户
     * @param {object} data - 租户数据
     * @returns {Promise} 创建结果
     */
    async createTenant(data) {
        return await getApi().post('/platform/tenants', data);
    },

    /**
     * 更新租户
     * @param {string} id - 租户ID
     * @param {object} data - 租户数据
     * @returns {Promise} 更新结果
     */
    async updateTenant(id, data) {
        return await getApi().put(`/platform/tenants/${id}`, data);
    },

    /**
     * 删除租户
     * @param {string} id - 租户ID
     * @returns {Promise} 删除结果
     */
    async deleteTenant(id) {
        return await getApi().delete(`/platform/tenants/${id}`);
    },

    /**
     * 获取平台统计信息
     * @returns {Promise} 统计数据
     */
    async getStatistics() {
        return await getApi().get('/platform/statistics');
    },

    /**
     * 获取审计日志列表
     * @param {object} params - 查询参数 {tenant_id, user_id, resource_type, operation_type, start_date, end_date, page, page_size}
     * @returns {Promise} 审计日志列表
     */
    async getAuditLogs(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.tenant_id) queryParams.append('tenant_id', params.tenant_id);
        if (params.user_id) queryParams.append('user_id', params.user_id);
        if (params.resource_type) queryParams.append('resource_type', params.resource_type);
        if (params.operation_type) queryParams.append('operation_type', params.operation_type);
        if (params.start_date) queryParams.append('start_date', params.start_date);
        if (params.end_date) queryParams.append('end_date', params.end_date);
        if (params.page) queryParams.append('skip', (params.page - 1) * (params.page_size || 100));
        if (params.page_size) queryParams.append('limit', params.page_size);
        
        const queryString = queryParams.toString();
        return await getApi().get(`/platform/audit-logs${queryString ? '?' + queryString : ''}`);
    },

    /**
     * 修改租户管理员密码
     * @param {string} tenantId - 租户ID
     * @param {string} newPassword - 新密码
     * @returns {Promise} 修改结果
     */
    async updateTenantAdminPassword(tenantId, newPassword) {
        return await getApi().post(`/platform/tenants/${tenantId}/admin-password`, {
            new_password: newPassword
        });
    }
};

window.PlatformAPI = PlatformAPI;

/**
 * 进销存管理API
 */
const InventoryAPI = {
    /**
     * 获取供应商列表
     * @param {object} params - 查询参数 {page, page_size, keyword, status}
     * @returns {Promise} 供应商列表 {items: [], pagination: {}}
     */
    async getSuppliers(params = {}) {
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 100,
            search: params.keyword || params.search || ''
        };
        if (params.status) backendParams.status = params.status;
        return await getApi().get('/inventory/suppliers', backendParams);
    },
    
    /**
     * 获取供应商详情
     * @param {string} id - 供应商ID
     * @returns {Promise} 供应商详情
     */
    async getSupplierDetail(id) {
        return await getApi().get(`/inventory/suppliers/${id}`);
    },
    
    /**
     * 创建供应商
     * @param {object} data - 供应商数据
     * @returns {Promise} 创建结果
     */
    async createSupplier(data) {
        return await getApi().post('/inventory/suppliers', data);
    },
    
    /**
     * 更新供应商
     * @param {string} id - 供应商ID
     * @param {object} data - 供应商数据
     * @returns {Promise} 更新结果
     */
    async updateSupplier(id, data) {
        return await getApi().put(`/inventory/suppliers/${id}`, data);
    },
    
    /**
     * 删除供应商
     * @param {string} id - 供应商ID
     * @returns {Promise} 删除结果
     */
    async deleteSupplier(id) {
        return await getApi().delete(`/inventory/suppliers/${id}`);
    },
    
    /**
     * 获取采购单列表
     * @param {object} params - 查询参数 {page, page_size, keyword, supplier_id, status, start_date, end_date}
     * @returns {Promise} 采购单列表 {items: [], pagination: {}}
     */
    async getPurchaseOrders(params = {}) {
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10,
            search: params.keyword || params.search || ''
        };
        if (params.supplier_id) backendParams.supplier_id = params.supplier_id;
        if (params.status) backendParams.status = params.status;
        if (params.start_date) backendParams.start_date = params.start_date;
        if (params.end_date) backendParams.end_date = params.end_date;
        return await getApi().get('/inventory/purchase-orders', backendParams);
    },
    
    /**
     * 获取采购单详情
     * @param {string} id - 采购单ID
     * @returns {Promise} 采购单详情
     */
    async getPurchaseOrderDetail(id) {
        return await getApi().get(`/inventory/purchase-orders/${id}`);
    },
    
    /**
     * 创建采购单
     * @param {object} data - 采购单数据
     * @returns {Promise} 创建结果
     */
    async createPurchaseOrder(data) {
        return await getApi().post('/inventory/purchase-orders', data);
    },
    
    /**
     * 更新采购单
     * @param {string} id - 采购单ID
     * @param {object} data - 采购单数据
     * @returns {Promise} 更新结果
     */
    async updatePurchaseOrder(id, data) {
        return await getApi().put(`/inventory/purchase-orders/${id}`, data);
    },
    
    /**
     * 审核采购单
     * @param {string} id - 采购单ID
     * @returns {Promise} 审核结果
     */
    async approvePurchaseOrder(id) {
        return await getApi().post(`/inventory/purchase-orders/${id}/approve`);
    },
    
    /**
     * 入库采购单
     * @param {string} id - 采购单ID
     * @returns {Promise} 入库结果
     */
    async receivePurchaseOrder(id) {
        return await getApi().post(`/inventory/purchase-orders/${id}/receive`);
    },
    
    /**
     * 删除采购单
     * @param {string} id - 采购单ID
     * @returns {Promise} 删除结果
     */
    async deletePurchaseOrder(id) {
        return await getApi().delete(`/inventory/purchase-orders/${id}`);
    },
    
    /**
     * 获取库存流水列表
     * @param {object} params - 查询参数 {page, page_size, drug_id, transaction_type, start_date, end_date}
     * @returns {Promise} 库存流水列表 {items: [], pagination: {}}
     */
    async getTransactions(params = {}) {
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10,
        };
        if (params.drug_id) backendParams.drug_id = params.drug_id;
        if (params.transaction_type) backendParams.transaction_type = params.transaction_type;
        if (params.start_date) backendParams.start_date = params.start_date;
        if (params.end_date) backendParams.end_date = params.end_date;
        return await getApi().get('/inventory/transactions', backendParams);
    },
    
    /**
     * 获取盘点单列表
     * @param {object} params - 查询参数 {page, page_size, status, start_date, end_date}
     * @returns {Promise} 盘点单列表 {items: [], pagination: {}}
     */
    async getInventoryChecks(params = {}) {
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10,
        };
        if (params.status) backendParams.status = params.status;
        if (params.start_date) backendParams.start_date = params.start_date;
        if (params.end_date) backendParams.end_date = params.end_date;
        return await getApi().get('/inventory/checks', backendParams);
    },
    
    /**
     * 获取盘点单详情
     * @param {string} id - 盘点单ID
     * @returns {Promise} 盘点单详情
     */
    async getInventoryCheckDetail(id) {
        return await getApi().get(`/inventory/checks/${id}`);
    },
    
    /**
     * 创建盘点单
     * @param {object} data - 盘点单数据
     * @returns {Promise} 创建结果
     */
    async createInventoryCheck(data) {
        return await getApi().post('/inventory/checks', data);
    },
    
    /**
     * 完成盘点
     * @param {string} id - 盘点单ID
     * @returns {Promise} 完成结果
     */
    async completeInventoryCheck(id) {
        return await getApi().post(`/inventory/checks/${id}/complete`);
    },
    
    /**
     * 删除盘点单
     * @param {string} id - 盘点单ID
     * @returns {Promise} 删除结果
     */
    async deleteInventoryCheck(id) {
        return await getApi().delete(`/inventory/checks/${id}`);
    },
    
    /**
     * 获取退货单列表
     * @param {object} params - 查询参数 {page, page_size, keyword, purchase_order_id, status, start_date, end_date}
     * @returns {Promise} 退货单列表 {items: [], pagination: {}}
     */
    async getReturnOrders(params = {}) {
        const backendParams = {
            skip: (params.page - 1) * params.page_size || 0,
            limit: params.page_size || 10,
            search: params.keyword || params.search || ''
        };
        if (params.purchase_order_id) backendParams.purchase_order_id = params.purchase_order_id;
        if (params.status) backendParams.status = params.status;
        if (params.start_date) backendParams.start_date = params.start_date;
        if (params.end_date) backendParams.end_date = params.end_date;
        return await getApi().get('/inventory/return-orders', backendParams);
    },
    
    /**
     * 获取退货单详情
     * @param {string} id - 退货单ID
     * @returns {Promise} 退货单详情
     */
    async getReturnOrderDetail(id) {
        return await getApi().get(`/inventory/return-orders/${id}`);
    },
    
    /**
     * 创建退货单
     * @param {object} data - 退货单数据
     * @returns {Promise} 创建结果
     */
    async createReturnOrder(data) {
        return await getApi().post('/inventory/return-orders', data);
    },
    
    /**
     * 更新退货单
     * @param {string} id - 退货单ID
     * @param {object} data - 退货单数据
     * @returns {Promise} 更新结果
     */
    async updateReturnOrder(id, data) {
        return await getApi().put(`/inventory/return-orders/${id}`, data);
    },
    
    /**
     * 审核退货单
     * @param {string} id - 退货单ID
     * @returns {Promise} 审核结果
     */
    async approveReturnOrder(id) {
        return await getApi().post(`/inventory/return-orders/${id}/approve`);
    },
    
    /**
     * 完成退货单
     * @param {string} id - 退货单ID
     * @returns {Promise} 完成结果
     */
    async completeReturnOrder(id) {
        return await getApi().post(`/inventory/return-orders/${id}/complete`);
    },
    
    /**
     * 取消退货单
     * @param {string} id - 退货单ID
     * @returns {Promise} 取消结果
     */
    async cancelReturnOrder(id) {
        return await getApi().post(`/inventory/return-orders/${id}/cancel`);
    },
    
    /**
     * 删除退货单
     * @param {string} id - 退货单ID
     * @returns {Promise} 删除结果
     */
    async deleteReturnOrder(id) {
        return await getApi().delete(`/inventory/return-orders/${id}`);
    },
    
    /**
     * 获取可退货的采购单信息
     * @param {string} purchase_order_id - 采购单ID
     * @returns {Promise} 可退货的采购单信息
     */
    async getReturnablePurchaseOrder(purchase_order_id) {
        return await getApi().get(`/inventory/purchase-orders/${purchase_order_id}/returnable`);
    }
};

/**
 * 打印模板API
 */
const PrintTemplateAPI = {
    /**
     * 获取打印模板列表
     * @param {object} params - 查询参数 {page, page_size, type}
     * @returns {Promise} 模板列表 {items: [], pagination: {}}
     */
    async getList(params = {}) {
        const backendParams = {
            skip: ((params.page || 1) - 1) * (params.page_size || 10),
            limit: params.page_size || 10
        };
        if (params.type) {
            backendParams.type = params.type;
        }
        return await getApi().get('/print-templates', backendParams);
    },
    
    /**
     * 获取打印模板详情
     * @param {string} id - 模板ID
     * @returns {Promise} 模板详情
     */
    async getDetail(id) {
        return await getApi().get(`/print-templates/${id}`);
    },
    
    /**
     * 创建打印模板
     * @param {object} data - 模板数据 {name, type, template_config, is_default}
     * @returns {Promise} 创建结果
     */
    async create(data) {
        return await getApi().post('/print-templates', data);
    },
    
    /**
     * 更新打印模板
     * @param {string} id - 模板ID
     * @param {object} data - 模板数据 {name, template_config, is_default}
     * @returns {Promise} 更新结果
     */
    async update(id, data) {
        return await getApi().put(`/print-templates/${id}`, data);
    },
    
    /**
     * 删除打印模板
     * @param {string} id - 模板ID
     * @returns {Promise} 删除结果
     */
    async delete(id) {
        return await getApi().delete(`/print-templates/${id}`);
    },
    
    /**
     * 设置默认模板
     * @param {string} id - 模板ID
     * @returns {Promise} 设置结果
     */
    async setDefault(id) {
        return await getApi().post(`/print-templates/${id}/set-default`);
    },
    
    /**
     * 预览打印模板
     * @param {string} id - 模板ID
     * @param {object} params - 预览参数 {data_type, data_id}
     * @returns {Promise} 预览HTML
     */
    async preview(id, params = {}) {
        const queryParams = {};
        if (params.data_type) queryParams.data_type = params.data_type;
        if (params.data_id) queryParams.data_id = params.data_id;
        return await getApi().get(`/print-templates/${id}/preview`, queryParams);
    },
    
    /**
     * 复制打印模板
     * @param {string} id - 模板ID
     * @param {string} newName - 新模板名称（可选）
     * @returns {Promise} 新创建的模板信息
     */
    async duplicate(id, newName = null) {
        const params = {};
        if (newName) {
            params.new_name = newName;
        }
        return await getApi().post(`/print-templates/${id}/duplicate`, null, params);
    },
    
    /**
     * 初始化预设模板
     * @returns {Promise} 创建的模板列表
     */
    async initPresetTemplates() {
        return await getApi().post('/print-templates/init-preset-templates');
    }
};

window.InventoryAPI = InventoryAPI;
window.PrintTemplateAPI = PrintTemplateAPI;
