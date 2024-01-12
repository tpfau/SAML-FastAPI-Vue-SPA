import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

type authedUser = {
  username: String
  token: String
}

export const useAuthStore = defineStore({
  id: 'authStore',
  state: () => ({
    user: null as null | authedUser,
    loggedIn: false as Boolean
  }),
  actions: {
    login(token: String) {
      if (token) {
        const claims = atob(token.split('.')[1])
        console.log(claims)
        this.user = { username: 'user', token: token }
        this.loggedIn = true
      } else {
        this.user = null
        this.loggedIn = false
      }
    }
  }
})
