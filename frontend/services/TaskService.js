app.service("TaskService", function ($http, AuthService) {

    var tasksUrl = "http://127.0.0.1:8000/api/tasks/";

    this.getTasks = function () {

        var token = AuthService.getAccessToken();

        return $http.get(tasksUrl, {
            headers: {
                Authorization: "Bearer " + token
            }
        });
    };
});