// for vue application in javascript files we dont need semi-colon at the end of the line
const app = Vue.createApp({
    // we can set any data, functions to react to events that we want to use in our app
    // template: '<h2>I am the template</h2>'
    data() {
        return {
            url: 'http://www.thenetninja.co.uk',
            showBooks: true,
            books: [
                { title: 'name of the wind', author: 'patrick rothfuss', img: 'assets/1.jpg'},
                { title: 'the way of kings', author: 'brandon sanderson', img: 'assets/2.jpg'},
                { title: 'the final empire', author: 'brandon sanderson', img: 'assets/3.jpg'}
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

