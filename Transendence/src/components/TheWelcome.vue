<script setup>
import WelcomeItem from './WelcomeItem.vue'
import SubjectIcon from './icons/IconSubject.vue'
import ToolingIcon from './icons/IconTooling.vue'
import EcosystemIcon from './icons/IconEcosystem.vue'
import CommunityIcon from './icons/IconCommunity.vue'
</script>

<template>
  <WelcomeItem>
    <template #icon>
      <SubjectIcon />
    </template>
    <template #heading>Subject</template>
    Transendence’s
    <a href="https://cdn.intra.42.fr/pdf/pdf/133398/en.subject.pdf" target="_blank" rel="noopener">official subject</a>
    provides you with all details and requirements needed for this project.
  </WelcomeItem>
  <WelcomeItem>
    <template #icon>
      <ToolingIcon />
    </template>
    <template #heading>Technologies & Features</template>
    This project leverages major technologies like <a href="https://www.djangoproject.com/" target="_blank" rel="noopener">Django</a> for backend functionality, ensuring high-level <a href="https://gdpr.eu/" target="_blank" rel="noopener">GDPR</a> compliance, <a href="https://jwt.io/" target="_blank" rel="noopener">JWT</a> for secure token authentication, and <a href="https://www.postgresql.org/" target="_blank" rel="noopener">PostgreSQL</a> for robust database management. Additionally, it includes game customization and a responsive, multilingual dashboard built with <a href="https://getbootstrap.com/" target="_blank" rel="noopener">Bootstrap</a> and JavaScript.
    <br />
    Refer to <code>README.md</code> for a complete setup guide.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <EcosystemIcon />
    </template>
    <template #heading>Ecosystem</template>
    Key components of Transcendence’s setup include:
    <a href="https://getbootstrap.com/" target="_blank" rel="noopener">Bootstrap</a> for styling and layout, integrated with 
    <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue.js</a>. For secure and dynamic backend operations, we use 
    <a href="https://www.djangoproject.com/" target="_blank" rel="noopener">Django</a>, paired with 
    <a href="https://www.postgresql.org/" target="_blank" rel="noopener">PostgreSQL</a> as our database. Enhanced security is ensured with GDPR compliance, 2FA, and JWT authentication.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <CommunityIcon />
    </template>
    <template #heading>Community Resources</template>
    Need help or inspiration? Connect with the developer community on
    <a href="https://discord.gg/programming" target="_blank" rel="noopener">Discord Programming Servers</a> or find support on 
    <a href="https://stackoverflow.com/questions/tagged/vue.js" target="_blank" rel="noopener">StackOverflow</a>. For Django-specific help, explore the 
    <a href="https://forum.djangoproject.com/" target="_blank" rel="noopener">Django Forum</a>. Stay updated with Vue and Django by following their official channels!
  </WelcomeItem>
</template>
