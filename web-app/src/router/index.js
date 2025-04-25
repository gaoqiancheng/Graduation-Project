import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import FileBrowser from '@/views/FileBrowser.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/browser',
    name: 'FileBrowser',
    component: FileBrowser,
    props: true // 允许通过路由传递props
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router