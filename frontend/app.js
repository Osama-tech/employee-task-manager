var app = angular.module("employeeApp", ["ngRoute"]);

app.config(function ($routeProvider, $locationProvider) {

    $locationProvider.hashPrefix("");

    $routeProvider
        .when("/login", {
            templateUrl: "views/login.html",
            controller: "LoginController"
        })

        .when("/tasks", {
            templateUrl: "views/tasks.html",
            controller: "TaskController",
            resolve: {
                auth: function (AuthService, $q) {

                    if (AuthService.isAuthenticated()) {
                        return true;
                    }

                    return $q.reject("Not authenticated");
                }
            }
        })

        .otherwise({
            redirectTo: "/login"
        });
});

app.run(function ($rootScope, $location) {

    $rootScope.$on(
        "$routeChangeError",
        function () {
            $location.path("/login");
        }
    );

});