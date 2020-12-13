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
                    for (var i = 0; i < Object.entries(response).length; i++){
                        var item = Object.entries(response)[i];
                        var k = item[0];
                        var v = item[1];
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

