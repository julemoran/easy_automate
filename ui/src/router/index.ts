import { createRouter, createWebHistory } from 'vue-router'


import PageEditor from '../pages/PageEditor.vue';
import EventsViewer from '../pages/EventsViewer.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/page-editor',
      name: 'PageEditor',
      component: PageEditor
    },
    {
      path: '/events-viewer',
      name: 'EventsViewer',
      component: EventsViewer
    },
    {
      path: '/',
      redirect: '/page-editor'
    }
  ],
})

export default router
