app.service("AuthService", function ($http) {

    var loginUrl =
        "http://127.0.0.1:8000/api/auth/login/";

    this.login = function (username, password) {

        return $http.post(loginUrl, {
            username: username,
            password: password
        });

    };

    this.saveTokens = function (access, refresh) {

        localStorage.setItem("access_token", access);
        localStorage.setItem("refresh_token", refresh);

    };

    this.getAccessToken = function () {

        return localStorage.getItem("access_token");

    };

    this.getRefreshToken = function () {

        return localStorage.getItem("refresh_token");

    };

    this.logout = function () {

        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

    };

    this.isAuthenticated = function () {

        return !!this.getAccessToken();
    
    };

});