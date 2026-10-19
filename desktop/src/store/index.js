import { useAppStore } from './modules/app'
import { useUserStore } from './modules/user'
import { usePermissionStore } from './modules/permission'
import { useSettingsStore } from './modules/settings'
import { useTagsViewStore } from './modules/tagsView'

export { useAppStore, useUserStore, usePermissionStore, useSettingsStore, useTagsViewStore }

export function resetAllStore() {
  useUserStore().resetState()
  usePermissionStore().resetState()
  useTagsViewStore().resetState()
}
