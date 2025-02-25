<script setup>
import { useI18n } from 'vue-i18n'
import WelcomeItem from './WelcomeItem.vue'
import SubjectIcon from './icons/IconSubject.vue'
import ToolingIcon from './icons/IconTooling.vue'
import EcosystemIcon from './icons/IconEcosystem.vue'
import CommunityIcon from './icons/IconCommunity.vue'

const { t, locale } = useI18n()

const languages = [
  { code: 'en', name: 'English' },
  { code: 'fr', name: 'Français' },
  { code: 'de', name: 'Deutsch' }
]
</script>

<template>
  <div class="language-selector">
    <select v-model="locale">
      <option v-for="lang in languages" :key="lang.code" :value="lang.code">
        {{ lang.name }}
      </option>
    </select>
  </div>

  <WelcomeItem>
    <template #icon>
      <SubjectIcon />
    </template>
    <template #heading>{{ t('welcome.subject.heading') }}</template>
    {{ t('welcome.subject.content') }}
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <ToolingIcon />
    </template>
    <template #heading>{{ t('welcome.technologies.heading') }}</template>
    {{ t('welcome.technologies.content') }}
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <EcosystemIcon />
    </template>
    <template #heading>{{ t('welcome.ecosystem.heading') }}</template>
    {{ t('welcome.ecosystem.content') }}
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <CommunityIcon />
    </template>
    <template #heading>{{ t('welcome.community.heading') }}</template>
    {{ t('welcome.community.content') }}
  </WelcomeItem>
</template>

<style scoped>
.language-selector {
  margin-bottom: 20px;
  text-align: right;
}

.language-selector select {
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
  background-color: white;
  font-size: 14px;
}
</style>