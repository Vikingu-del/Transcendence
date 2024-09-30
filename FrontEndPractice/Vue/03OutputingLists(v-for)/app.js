// for vue application in javascript files we dont need semi-colon at the end of the line
const app = Vue.createApp({
    // we can set any data, functions to react to events that we want to use in our app
    // template: '<h2>I am the template</h2>'
    data() {
        return {
            showBooks: true,
            books: [
                { title: 'name of the wind', author: 'patrick rothfuss'},
                { title: 'the way of kings', author: 'brandon sanderson'},
                { title: 'the final empire', author: 'brandon sanderson'},
            ]
        }
    },
    methods: {
        toggleShowBooks() {
            this.showBooks = !this.showBooks
        }
    }
})

app.mount('#app') // this will mount the app to the div with id app

