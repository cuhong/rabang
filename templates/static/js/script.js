var auth = {
    "login": function login(username, password, successCallback, errorCallback, next=null) {
        $.ajax({
            type: "POST",
            url: "/api/account/login/",
            data: {
                'username': username,
                'password': password,
                'next': next
            },
            dataType: "json",
            success: function (response) {
                for (var [k, v] of Object.entries(response)) {
                    window.localStorage.setItem(k, v)
                }
                successCallback(response)
            },
            error: function (response, status, error) {
                errorCallback()
            },
        });
    }

}

