// app.controller(
//     "TaskController",
//     function ($scope, TaskService, AuthService) {

//         $scope.title = "Employee Task Manager";

//         $scope.tasks = [];

//         $scope.loginData = {
//             username: "",
//             password: ""
//         };

//         $scope.loginError = "";

//         $scope.login = function () {

//             AuthService.login(
//                 $scope.loginData.username,
//                 $scope.loginData.password
//             )
//             .then(function (response) {

//                 AuthService.saveTokens(
//                     response.data.access,
//                     response.data.refresh
//                 );

//                 $scope.loginError = "";

//                 $scope.loadTasks();

//             })
//             .catch(function (error) {

//                 console.error("Login failed:", error);

//                 $scope.loginError =
//                     "Invalid username or password.";

//             });

//         };

//         $scope.loadTasks = function () {

//             TaskService.getTasks()
//                 .then(function (response) {

//                     $scope.tasks = response.data || response.data;

//                 })
//                 .catch(function (error) {

//                     console.error("Loading tasks failed:", error);

//                 });

//         };

//     }
// );


app.controller(
    "TaskController",
    function ($scope, TaskService) {

        $scope.title = "Employee Task Manager";

        $scope.tasks = [];

        $scope.loadTasks = function () {

            TaskService.getTasks()

                .then(function (response) {

                    $scope.tasks =
                        response.data.results || response.data;

                })

                .catch(function (error) {

                    console.error(error);

                });

        };

        $scope.completeTask = function (task) {

            task.status = "Completed";

        };

        $scope.loadTasks();

    }
);