import store from '@/store';

export const auth = {
    /**
     * Set authentication token
     * @param {string} token - JWT token
     */
    // setToken(token) {
    //     localStorage.setItem('token', token);
    // },
    setToken(token) {
        store.dispatch('loginAction', token);
    },

    /**
     * Get current token
     * @returns {string|null} token
     */
    // getToken() {
    //     return localStorage.getItem('token');
    // },
    getToken() {
        return store.getters.getToken;
    },
    
    /**
     * Remove token and clear auth state
     */
    // removeToken() {
    //     localStorage.removeItem('token');
    // },
    async logout() {
        await store.dispatch('logoutAction');
    },
    
    /**
     * Check if user is authenticated
     * @returns {boolean}
     */
    // isAuthenticated() {
    //     return !!this.getToken();
    // }
    isAuthenticated() {
        return store.getters.isAuthenticated;
    },

    /**
     * Check if token is expired
     * @returns {boolean}
     */
    isTokenExpired() {
        const token = this.getToken();
        if (!token) {
            return true;
        }

        try {
            // JWT tokens have 3 parts separated by dots: header.payload.signature
            // Example token: eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiam9obiIsImV4cCI6MTYxNjE4MjM5MH0.rTiEkYxCnxJ4AQ7YFZW7SLnqGYwD0LYXZ6qzRe6zT9c

            // Split token and get payload (second part)
            const parts = token.split('.'); // ['eyJhbGciOiJIUzI1NiJ9', 'eyJ1c2VyIjoiam9obiIsImV4cCI6MTYxNjE4MjM5MH0', 'rTiEkYxCnxJ4AQ7YFZW7SLnqGYwD0LYXZ6qzRe6zT9c']
            const payloadBase64 = parts[1]; // 'eyJ1c2VyIjoiam9obiIsImV4cCI6MTYxNjE4MjM5MH0'

            // atob() decodes a base64 encoded string
            // Base 64 is an encoding scheme that converts binary data into plain text using 64 charachters A-Z, a-z, 0-9, +, / and = (padding)
            const payloadJson = atob(payloadBase64); // '{"user":"john","exp":1616182390}' 
            const payload = JSON.parse(payloadJson); // { user: 'john', exp: 1616182390 }

            // the complete flow of conversion
            // Base64 String -> (atob) -> JSON String -> (JSON.parse) -> JavaScript Object

            // const payload = JSON.parse(atob(token.split('.')[1]));

            // Check if token is expired
            // exp is Unix timestamp in seconds (seconds since 1970)
            // Date.now() returns milliseconds since 1970, so divide by 1000 to get seconds
            return payload.exp < Date.now() / 1000;
        } catch {
            return true;
        }
    }
};

export default auth;