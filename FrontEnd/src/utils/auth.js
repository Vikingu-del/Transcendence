export const auth = {
    setToken(token) {
        localStorage.setItem('token', token);
    },
    
    getToken() {
        return localStorage.getItem('token');
    },
    
    removeToken() {
        localStorage.removeItem('token');
    },
    
    isAuthenticated() {
        return !!this.getToken();
    }
};

export default auth;