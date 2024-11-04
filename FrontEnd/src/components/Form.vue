<template>
    <form @submit.prevent="handleSubmit">
        <div v-if="formType === 'register'">
            <label for="email">Email</label>
            <input id="email" type="email" v-model="email" />
        </div>
        <label for="username">Username</label>
        <input id="username" v-model="username">

        <label for="password">Password</label>
        <input id="password" type="password" v-model="password">

        <button type="submit">{{ formType === 'login' ? 'Login' : 'Register' }}</button>
    </form>
</template>

<script>
export default {
    props: [ 'formType' ],
    data() {
        return {
            username: '',
            password: '',
            email: '',
        };
    },
    methods: {
        handleSubmit() {
            console.log(this.username, this.password, this.email);
            if (this.formType === 'login') {
                // login
            } else {
                // register
            }
        },
    },
};
</script>

<style scoped>
    form {
        margin-top: 2rem;
        display: flex;
        flex-flow: column;
        position: relative;
        place-items: center;
        place-content: center;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 0.4rem;
        color: var(--color-text);
    }

    input {
        margin-top: 1rem;
        margin-bottom: 2rem;
        padding: 0.51rem;
        border-radius: 0.25rem;
    }

    div {
        display: flex;
        flex-flow: column;
        place-items: center;
    }

    button {
        padding: 0.51rem;
        border-radius: 0.25rem;
        cursor: pointer;
    }
</style>