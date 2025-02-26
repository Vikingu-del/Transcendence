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
    {{ t('welcome.subject.content1') }} <a href="https://cdn.intra.42.fr/pdf/pdf/133398/en.subject.pdf" target="_blank" rel="noopener">
    {{ t('welcome.subject.link') }} </a> {{ t('welcome.subject.content2') }}
  </WelcomeItem>
  <WelcomeItem>
    <template #icon>
      <ToolingIcon />
    </template>
    <template #heading>{{ t('welcome.technologies.heading') }}</template>
    {{ t('welcome.technologies.content1') }} <a href="https://www.djangoproject.com/" target="_blank" rel="noopener">{{ t('welcome.technologies.django') }} </a> {{ t('welcome.technologies.content2') }} <a href="https://gdpr.eu/" target="_blank" rel="noopener">{{ t('welcome.technologies.gdpr') }} </a> {{ t('welcome.technologies.content3') }} <a href="https://jwt.io/" target="_blank" rel="noopener">{{ t('welcome.technologies.jwt') }}</a> {{ t('welcome.technologies.content4') }} <a href="https://www.postgresql.org/" target="_blank" rel="noopener">{{ t('welcome.technologies.postgresql') }} </a> {{ t('welcome.technologies.content5') }} <a href="https://getbootstrap.com/" target="_blank" rel="noopener">{{ t('welcome.technologies.bootstrap') }}</a> {{ t('welcome.technologies.content6') }}
    <br />
    {{ t('welcome.technologies.content7') }}
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <EcosystemIcon />
    </template>
    <template #heading>{{t('welcome.ecosystem.heading')}}</template>
    {{ t('welcome.ecosystem.content') }}
    <a href="https://getbootstrap.com/" target="_blank" rel="noopener">{{ t('welcome.ecosystem.bootstrap') }}</a> {{ t('welcome.ecosystem.content1') }}
    <a href="https://vuejs.org/" target="_blank" rel="noopener">{{t('welcome.ecosystem.vue')}}</a>{{t('welcome.ecosystem.content2')}}
    <a href="https://www.djangoproject.com/" target="_blank" rel="noopener">{{t('welcome.ecosystem.django')}}</a>{{t('welcome.ecosystem.content3')}}
    <a href="https://www.postgresql.org/" target="_blank" rel="noopener">{{t('welcome.ecosystem.postgresql')}}</a>{{t('welcome.ecosystem.content4')}}
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <CommunityIcon />
    </template>
    <template #heading>{{ t('welcome.community.heading') }}</template>
    {{ t('welcome.community.content') }}
    <a href="https://discord.gg/programming" target="_blank" rel="noopener">{{ t('welcome.community.discord') }}</a> {{ t('welcome.community.content1') }}
    <a href="https://stackoverflow.com/questions/tagged/vue.js" target="_blank" rel="noopener">{{ t('welcome.community.stackoverflow') }}</a>{{ t('welcome.community.content2') }}
    <a href="https://forum.djangoproject.com/" target="_blank" rel="noopener">{{ t('welcome.community.django') }}</a>{{ t('welcome.community.content3') }}
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