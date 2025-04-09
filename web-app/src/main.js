import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);

app.use(router);

// 开启 Vue 开发模式
app.config.debug = true;
app.config.warnHandler = (msg, vm, trace) => {
  console.warn(`[Vue warn]: ${msg} ${trace}`);
};

app.mount('#app');
