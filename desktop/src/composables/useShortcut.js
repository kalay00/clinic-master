import { onMounted, onUnmounted } from 'vue'

export function useShortcut(shortcuts) {
  const handleKeydown = (event) => {
    const key = event.key.toLowerCase()
    const ctrl = event.ctrlKey || event.metaKey
    const shift = event.shiftKey
    const alt = event.altKey
    
    for (const shortcut of shortcuts) {
      const matchKey = shortcut.key.toLowerCase() === key
      const matchCtrl = shortcut.ctrl ? ctrl : !ctrl
      const matchShift = shortcut.shift ? shift : !shift
      const matchAlt = shortcut.alt ? alt : !alt
      
      if (matchKey && matchCtrl && matchShift && matchAlt) {
        event.preventDefault()
        shortcut.action()
        break
      }
    }
  }
  
  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
  })
  
  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
  })
}

export const defaultShortcuts = [
  { key: 'k', ctrl: true, action: () => {} },
  { key: 'f', ctrl: true, action: () => {} },
  { key: 'r', ctrl: true, action: () => {} },
  { key: 'w', ctrl: true, action: () => {} },
  { key: 't', ctrl: true, action: () => {} }
]
