<script setup>
import TheWelcome from '../components/TheWelcome.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <main>
    <h1>{{ t('home.title') }}</h1>
    <p>{{ t('home.description') }}</p>
    <TheWelcome />
  </main>
</template>

<style scoped>
main {
  padding: 2rem;
}

h1 {
  font-size: 2em;
  margin-bottom: 1rem;
  text-align: center;
}

p {
  text-align: center;
  margin-bottom: 2rem;
}
</style>
