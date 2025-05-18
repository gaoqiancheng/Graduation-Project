import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import FileBrowser from '@/views/FileBrowser.vue'
import CreateFile from '@/views/CreateFile.vue'

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
  },
  {
    path: '/create',
    name: 'CreateFile',
    component: CreateFile
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router