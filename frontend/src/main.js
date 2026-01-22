import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

// Vant UI (Importing needed components globally or can be done on demand)
import { Button, Dialog, Field, CellGroup, Form, Toast, Popup } from 'vant'
import 'vant/lib/index.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.use(Button)
app.use(Dialog)
app.use(Field)
app.use(CellGroup)
app.use(Form)
app.use(Toast)
app.use(Popup)

app.mount('#app')
