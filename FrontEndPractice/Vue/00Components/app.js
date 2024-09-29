// for vue application in javascript files we dont need semi-colon at the end of the line
const app = Vue.createApp({
    // we can set any data, functions to react to events that we want to use in our app
    // template: '<h2>I am the template</h2>'
    data() {
        return {
            title: 'The Final Empire',
            author: 'Brandon Sanderson',
            age: 45
        }
    },
    methods: {
        changeTitle(title) {
            // this.title = 'Words of Radiance'
            this.title = title
        }
    }
})

app.mount('#app') // this will mount the app to the div with id app

