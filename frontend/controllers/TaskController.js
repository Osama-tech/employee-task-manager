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