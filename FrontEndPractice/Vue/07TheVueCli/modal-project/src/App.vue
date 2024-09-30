  <template>
    <div>
      <h1>{{ title }}</h1>
      <!-- <input type="text" ref="name"> -->
      <!-- <button @click="handleClick">click me</button> -->
       <p>Welcome</p>
       <div v-if="showModal">
         <!-- We can init a componet with PROPS <Modal :header="header" :text="text" :theme="theme" @close="toggleModal" /> -->
        <Modal theme="sale" @close="toggleModal" > <!--- Passing a template to component is called slot--->
          <template v-slot:links>
            <a href="#">Sign up now</a>
            <a href="#">More info</a>
          </template>
          <h1>{{ header }}</h1>
          <p>{{ text }}</p>
        </Modal>
       </div>
       <button @click.alt="toggleModal">open modal alt</button>
    </div>
  </template>

<!-- 
  Challenge
      - create an extra button to open a different modal
      - use the same modal component bu t pass in a different template (slot)
      - use a different method (e.g. toogleModalTwo) and data (e.g. showModalTwo)
-->

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
    }
  },
  methods: {
    toggleModal() {
      this.showModal = !this.showModal
    }
    // handleClick() {
    //   console.log(this.$refs.name)
    //   this.$refs.name.classList.add('active')
    //   this.$refs.name.focus()
    // }
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
