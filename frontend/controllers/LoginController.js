app.controller(
    "LoginController",
    function ($scope, AuthService, $location) {

        $scope.loginData = {
            username: "",
            password: ""
        };

        $scope.error = "";
        $scope.isLoading = false;

        $scope.login = function () {

            $scope.error = "";
            $scope.isLoading = true;

            AuthService.login(
                $scope.loginData.username,
                $scope.loginData.password
            )
            .then(function (response) {

                AuthService.saveTokens(
                    response.data.access,
                    response.data.refresh
                );

                $location.path("/tasks");

            })
            .catch(function (error) {

                console.error(error);

                $scope.error =
                    "Invalid username or password.";

            })
            .finally(function () {

                $scope.isLoading = false;

            });

        };

    }
);