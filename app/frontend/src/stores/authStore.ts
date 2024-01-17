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
    loggedIn: false as Boolean,
    rerouting: false
  }),
  actions: {
    async login(token: String) {
      if (token) {
        const claims = atob(token.split('.')[1])
        console.log(claims)
        this.user = { username: 'user', token: token }
        await fetch('/auth/test', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
            // You may need to add additional headers like authorization if required
          },
          body: JSON.stringify({ token: token })
        })
          .then((response) => response.json())
          .then((result) => {
            if (result.authed) {
              this.user = { username: result.user, token: token }
              this.loggedIn = true
            } else {
              console.log('Not / no longer authed')
              this.loggedIn = false
              this.user = null
            }
          })
          .catch((err) => {
            console.error(err)
          })
      } else {
        this.user = null
        this.loggedIn = false
      }
    }
  }
})
