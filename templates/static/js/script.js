var auth = {
    "login": function login(username, password, successCallback, errorCallback, next = null) {
        if (window.localStorage.getItem("rabangToken")) {
            if (next) {
                window.location = next;
            } else {
                window.location = '/';
            }
        } else {
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
                        if (k === "key") {
                            window.localStorage.setItem("rabangToken", v);
                        } else {
                            window.localStorage.setItem(k, v);
                        }
                    }
                    successCallback(response);
                },
                error: function (response, status, error) {
                    errorCallback();
                },
            });
        }
    },
    "logout": function () {
        window.localStorage.clear();
        window.location = '/';
    }
};

