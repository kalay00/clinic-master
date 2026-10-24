import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

/**
 * 表格内部滚动（固定高度布局）
 *
 * 背景：el-table 的 height="100%" 不会计算内部 body 高度（EP 只对数值 height
 * 做内部布局），且 flex 子项默认只缩不增，表格高度会卡在初始测量值。
 * 用法：测量包裹容器（.table-wrap，flex:1）的剩余高度，绑定为数值 height。
 *
 * 模板：
 *   <div class="table-wrap" ref="wrapRef">
 *     <el-table ref="tableRef" :height="tableHeight" ...>
 * 脚本：
 *   const { wrapRef, tableRef, tableHeight, refresh } = useTableHeight()
 *   数据加载完成后调用 refresh() 刷新滚动状态
 */
export function useTableHeight() {
  const wrapRef = ref(null)
  const tableRef = ref(null)
  const tableHeight = ref(400)
  let observer = null

  const refresh = async () => {
    const el = wrapRef.value
    if (el && el.clientHeight) tableHeight.value = el.clientHeight
    // 高度/数据变化后主动刷新 EP 内部布局，否则 body-wrapper 滚动状态不更新
    await nextTick()
    tableRef.value?.doLayout?.()
  }

  onMounted(() => {
    refresh()
    if (typeof ResizeObserver !== 'undefined' && wrapRef.value) {
      observer = new ResizeObserver(refresh)
      observer.observe(wrapRef.value)
    }
  })

  onBeforeUnmount(() => {
    if (observer) {
      observer.disconnect()
      observer = null
    }
  })

  return { wrapRef, tableRef, tableHeight, refresh }
}
