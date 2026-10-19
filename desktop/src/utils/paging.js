/**
 * 后端列表接口单页上限为 100，超过会返回 422。
 * 需要一次性取全量数据（下拉选项、批量加载等）时，用本方法分页拉取直至取完。
 *
 * @param {Function} fetcher 形如 ({ page, page_size }) => Promise<{ items, total }> 的请求函数
 * @param {Object}   options
 * @param {number}   options.size   每页条数，默认 100（后端上限）
 * @param {number}   options.maxPages 安全上限，防止接口异常时死循环，默认 20
 * @returns {Promise<Array>} 合并后的全部条目
 */
export async function fetchAllPages(fetcher, options = {}) {
  const { size = 100, maxPages = 20 } = options
  const all = []
  let page = 1
  for (;;) {
    const res = await fetcher({ page, page_size: size })
    const items = res?.items || []
    all.push(...items)
    const total = Number(res?.total ?? 0)
    if (!items.length || all.length >= total || items.length < size || page >= maxPages) break
    page += 1
  }
  return all
}

export default { fetchAllPages }
