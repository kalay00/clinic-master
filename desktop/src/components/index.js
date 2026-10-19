import { defineAsyncComponent } from 'vue'

const modules = import.meta.glob('./**/*.vue', { eager: true })

export default {
  install(app) {
    Object.keys(modules).forEach(path => {
      const component = modules[path]
      const componentName = path
        .replace(/^\.\//, '')
        .replace(/\.vue$/, '')
        .split('/')
        .pop()
      if (componentName && component.default) {
        app.component(componentName, component.default || component)
      }
    })
  }
}
