import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../App.vue')
  },
  {
    path: '/:catchAll(.*)*',
    redirect: '/'
  }
]

export default routes
