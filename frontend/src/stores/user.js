import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref(JSON.parse(localStorage.getItem('user_info')) || null)

  function randomColor() {
    // generate pastel-ish color
    const hue = Math.floor(Math.random() * 360)
    return `hsl(${hue} 70% 45%)`
  }

  function login(nickname) {
    const newUser = { 
      id: Date.now().toString(), 
      name: nickname || `红脉卫士_${Math.floor(Math.random()*1000)}`,
      color: randomColor()
    }
    userInfo.value = newUser
    localStorage.setItem('user_info', JSON.stringify(newUser))
  }

  function setColor(color) {
    if (!userInfo.value) return
    userInfo.value.color = color
    localStorage.setItem('user_info', JSON.stringify(userInfo.value))
  }

  function setName(name) {
    if (!userInfo.value) return
    userInfo.value.name = name
    localStorage.setItem('user_info', JSON.stringify(userInfo.value))
  }

  function checkLogin() {
    return !!userInfo.value
  }

  return { userInfo, login, checkLogin, setColor, setName }
})
