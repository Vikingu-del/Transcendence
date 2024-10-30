<script setup>
  import Form from '../components/Form.vue'
</script>

<template>
  <main>
      <h1>Register</h1>
      <Form formType="register" />
  </main>
</template>

<style scoped>
    main {
        display: flex;
        flex-flow: column;
        place-items: center;
        place-content: center;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 0.4rem;
        color: var(--color-text);
    }
</style>
