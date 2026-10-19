import * as XLSX from 'xlsx'

export function exportToExcel(data, columns, filename = '导出数据') {
  const headers = columns.map(col => col.label || col.prop)
  const keys = columns.map(col => col.prop)
  
  const worksheetData = data.map(row => 
    keys.map(key => {
      const value = row[key]
      if (typeof value === 'boolean') {
        return value ? '是' : '否'
      }
      return value || ''
    })
  )
  
  worksheetData.unshift(headers)
  
  const workbook = XLSX.utils.book_new()
  const worksheet = XLSX.utils.aoa_to_sheet(worksheetData)
  
  worksheet['!cols'] = columns.map(col => ({
    wch: col.width || 15
  }))
  
  XLSX.utils.book_append_sheet(workbook, worksheet, '数据')
  
  XLSX.writeFile(workbook, `${filename}.xlsx`)
}

export function exportToCSV(data, columns, filename = '导出数据') {
  const headers = columns.map(col => col.label || col.prop).join(',')
  const keys = columns.map(col => col.prop)
  
  const rows = data.map(row => 
    keys.map(key => {
      const value = row[key]
      if (typeof value === 'boolean') {
        return value ? '是' : '否'
      }
      const strValue = String(value || '')
      return strValue.includes(',') ? `"${strValue}"` : strValue
    }).join(',')
  )
  
  const csvContent = `${headers}\n${rows.join('\n')}`
  
  const blob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}.csv`)
  link.style.visibility = 'hidden'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
