<!-- 
  Challenge
      - create an extra button to open a different modal
      - use the same modal component bu t pass in a different template (slot)
      - use a different method (e.g. toogleModalTwo) and data (e.g. showModalTwo)
-->

<template>
  <div>
    <h1>{{ title }}</h1>
     <p>Welcome</p>
     <teleport to=".modals" v-if="showModal">
      <Modal theme="sale" @close="toggleModal" >
        <template v-slot:links>
          <a href="#">Sign up now</a>
          <a href="#">More info</a>
        </template>
        <h1>{{ header }}</h1>
        <p>{{ text }}</p>
      </Modal>
     </teleport>
     <teleport to=".modals" v-if="showModalTwo">
      <Modal @close="toggleModalTwo" >
        <h1>Sign up to the newsletter</h1>
        <p>For updates and promo codes!</p>
      </Modal>
     </teleport>
     <button @click.alt="toggleModal">open modal1</button>
     <button @click="toggleModalTwo">op modal2</button>
  </div>
</template>

<script>
import Modal from './components/Modal.vue'

export default {
name: 'App',
components: {
  Modal
},
data() {
  return {
    title: 'My First Vue App :)',
    header: 'Sign up for the Giveaway!',
    text: 'Grab your ninja swag for half price!',
    theme: 'sale',
    showModal: false,
    showModalTwo: false
  }
},
methods: {
  toggleModal() {
    this.showModal = !this.showModal
  },
  toggleModalTwo() {
    this.showModalTwo = !this.showModalTwo
  }
}
}
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 10px;
}
h1 {
  border-bottom: 1px solid #ddd;
  display: inline-block;
  padding-bottom: 10px;
}
</style>
