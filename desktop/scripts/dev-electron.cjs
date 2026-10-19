const { spawn } = require('child_process')
const path = require('path')
const http = require('http')
const net = require('net')

let viteProcess = null
let electronProcess = null

console.log('========================================')
console.log('  华宣诊所管理系统 - 开发模式启动')
console.log('========================================')
console.log()

/**
 * 检测某个端口是否已被占用
 */
function isPortInUse(port) {
  return new Promise((resolve) => {
    const client = net.createConnection({ port, host: 'localhost' }, () => {
      client.destroy()
      resolve(true)
    })
    client.on('error', () => {
      client.destroy()
      resolve(false)
    })
  })
}

/**
 * 扫描范围端口，找到第一个返回 HTTP 200 的 Vite 服务器端口
 */
async function findVitePort(startPort = 5173, maxPort = 5200) {
  for (let port = startPort; port <= maxPort; port++) {
    const isListening = await isPortInUse(port)
    if (isListening) {
      const isVite = await checkIsViteServer(port)
      if (isVite) {
        return port
      }
    }
  }
  return null
}

/**
 * 检查端口上的服务是否是 Vite 服务器
 */
function checkIsViteServer(port) {
  return new Promise((resolve) => {
    const req = http.get(`http://localhost:${port}`, { timeout: 2000 }, (res) => {
      resolve(res.statusCode === 200 || res.statusCode === 302)
    })
    req.on('error', () => resolve(false))
    req.on('timeout', () => { req.destroy(); resolve(false) })
    req.end()
  })
}

/**
 * 等待 Vite 启动完成
 */
function waitForViteReady(maxRetries = 30, interval = 1000) {
  return new Promise(async (resolve, reject) => {
    let retries = 0
    const check = async () => {
      if (retries >= maxRetries) {
        reject(new Error('Vite 启动超时'))
        return
      }
      const port = await findVitePort()
      if (port) {
        resolve(port)
        return
      }
      retries++
      setTimeout(check, interval)
    }
    check()
  })
}

/**
 * 启动 Vite
 */
function startVite() {
  console.log('[1/2] 启动 Vite 开发服务器...')
  return new Promise((resolve, reject) => {
    viteProcess = spawn('npx', ['vite'], {
      cwd: process.cwd(),
      stdio: 'inherit',
      env: {
        ...process.env,
        NODE_ENV: 'development'
      },
      shell: true
    })

    viteProcess.on('error', (err) => {
      console.error('Vite 启动失败:', err)
      reject(err)
    })

    viteProcess.on('exit', (code) => {
      console.log('Vite 进程退出，代码:', code)
      process.exit(code)
    })

    // 等待 Vite 启动并检测实际端口
    waitForViteReady()
      .then((port) => {
        console.log('✅ Vite 开发服务器已就绪，端口:', port)
        resolve(port)
      })
      .catch((err) => reject(err))
  })
}

/**
 * 启动 Electron
 */
function startElectron(vitePort) {
  console.log()
  console.log('[2/2] 启动 Electron...')

  const viteUrl = `http://localhost:${vitePort}`
  const electronPath = path.join(__dirname, '../node_modules/electron/dist/electron.exe')
  const mainPath = path.join(__dirname, '../electron/main.cjs')

  console.log('  Electron 路径:', electronPath)
  console.log('  主进程文件:', mainPath)
  console.log('  Vite 服务地址:', viteUrl)

  electronProcess = spawn(electronPath, [mainPath], {
    cwd: process.cwd(),
    stdio: ['pipe', 'pipe', 'pipe'],
    env: {
      ...process.env,
      NODE_ENV: 'development',
      VITE_DEV_SERVER_URL: viteUrl,
      ELECTRON_ENABLE_LOGGING: '1'
    }
  })

  electronProcess.stdout.on('data', (data) => {
    process.stdout.write('[Electron] ' + data.toString())
  })

  electronProcess.stderr.on('data', (data) => {
    process.stderr.write('[Electron Error] ' + data.toString())
  })

  electronProcess.on('error', (err) => {
    console.error('Electron 启动失败:', err)
    process.exit(1)
  })

  electronProcess.on('exit', (code) => {
    console.log('Electron 进程退出，代码:', code)
    if (viteProcess) {
      viteProcess.kill()
    }
    process.exit(code)
  })

  console.log()
  console.log('========================================')
  console.log('  开发环境已就绪！')
  console.log('  Vite: ' + viteUrl)
  console.log('  按 Ctrl+C 退出')
  console.log('========================================')
}

// 清理进程
process.on('SIGINT', () => {
  console.log('\n正在退出...')
  if (viteProcess) viteProcess.kill()
  if (electronProcess) electronProcess.kill()
  process.exit(0)
})

process.on('SIGTERM', () => {
  if (viteProcess) viteProcess.kill()
  if (electronProcess) electronProcess.kill()
  process.exit(0)
})

// 启动流程
startVite()
  .then((port) => startElectron(port))
  .catch((err) => {
    console.error('启动失败:', err)
    process.exit(1)
  })
