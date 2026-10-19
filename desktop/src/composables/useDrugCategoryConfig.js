import { ref } from 'vue'
import { getTenantConfig } from '@/api/tenant'

/**
 * 药品分类（西药 / 中药）启用开关
 * 来源于「设置 - 基础设置 - 药品设置」，租户级配置。
 *
 * 配置读取失败时默认全部启用，避免阻塞业务页面。
 * 多个页面共用同一次请求结果（模块级缓存）。
 */
const westernEnabled = ref(true)
const chineseEnabled = ref(true)
let loaded = false
let pending = null

async function load() {
  if (loaded) return
  if (pending) return pending
  pending = (async () => {
    try {
      const cfg = await getTenantConfig()
      const dc = cfg?.drug_category || {}
      westernEnabled.value = dc.western_enabled !== false
      chineseEnabled.value = dc.chinese_enabled !== false
    } catch {
      westernEnabled.value = true
      chineseEnabled.value = true
    } finally {
      loaded = true
      pending = null
    }
  })()
  return pending
}

/** 配置变更后（如基础设置保存成功）清空缓存，下次访问重新拉取 */
function refresh() {
  loaded = false
  pending = null
  return load()
}

export function useDrugCategoryConfig() {
  return { westernEnabled, chineseEnabled, load, refresh }
}

export default { useDrugCategoryConfig }
