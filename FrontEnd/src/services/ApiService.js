export const getBaseUrl = () => {
    // Always use the NGINX_HOST for API requests
    return `${window.location.protocol}//${window.location.hostname}`;
};

export const getApiEndpoints = (baseUrl) => ({
    profile: `${baseUrl}/api/user/profile/`,
    search: `${baseUrl}/api/user/profile/search/`,
    friendRequests: `${baseUrl}/api/user/profile/friend-requests/`,
    chat: `${baseUrl}/api/chat/`,
    media: `${baseUrl}/api/user/media/`
});

export const getAuthEndpoints = (baseUrl) => ({
    register: `${baseUrl}/api/user/register/`,
    login: `${baseUrl}/api/user/login/`,
    logout: `${baseUrl}/api/user/logout/`,
    token: `${baseUrl}/api/user/token/`
});