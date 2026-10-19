import Cookies from 'js-cookie'

const STORAGE_PREFIX = 'zzy_electron_'

function getKey(key) {
  return STORAGE_PREFIX + key
}

export const storage = {
  set(key, value, expires) {
    try {
      const data = {
        value,
        timestamp: Date.now(),
        expires: expires ? Date.now() + expires * 1000 : null
      }
      localStorage.setItem(getKey(key), JSON.stringify(data))
      return true
    } catch (e) {
      console.error('storage set error:', e)
      return false
    }
  },

  get(key) {
    try {
      const str = localStorage.getItem(getKey(key))
      if (!str) return null
      const data = JSON.parse(str)
      if (data.expires && Date.now() > data.expires) {
        this.remove(key)
        return null
      }
      return data.value
    } catch (e) {
      console.error('storage get error:', e)
      return null
    }
  },

  remove(key) {
    try {
      localStorage.removeItem(getKey(key))
      return true
    } catch (e) {
      console.error('storage remove error:', e)
      return false
    }
  },

  clear() {
    try {
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith(STORAGE_PREFIX)) {
          localStorage.removeItem(key)
        }
      })
      return true
    } catch (e) {
      console.error('storage clear error:', e)
      return false
    }
  },

  has(key) {
    return this.get(key) !== null
  }
}

export const cookie = {
  set(key, value, options = {}) {
    return Cookies.set(getKey(key), value, options)
  },

  get(key) {
    return Cookies.get(getKey(key))
  },

  remove(key) {
    return Cookies.remove(getKey(key))
  },

  clear() {
    const keys = Object.keys(Cookies.get())
    keys.forEach(key => {
      if (key.startsWith(STORAGE_PREFIX)) {
        Cookies.remove(key)
      }
    })
  }
}

export const session = {
  set(key, value) {
    try {
      sessionStorage.setItem(getKey(key), JSON.stringify(value))
      return true
    } catch (e) {
      console.error('session set error:', e)
      return false
    }
  },

  get(key) {
    try {
      const str = sessionStorage.getItem(getKey(key))
      return str ? JSON.parse(str) : null
    } catch (e) {
      console.error('session get error:', e)
      return null
    }
  },

  remove(key) {
    try {
      sessionStorage.removeItem(getKey(key))
      return true
    } catch (e) {
      console.error('session remove error:', e)
      return false
    }
  },

  clear() {
    try {
      sessionStorage.clear()
      return true
    } catch (e) {
      console.error('session clear error:', e)
      return false
    }
  }
}

export default storage
