function registerKey(uid, card_name, successCallback, errorCallback) {
    $.ajax({
        type: "POST",
        url: "{% url 'payment_api:register' %}",
        data: {
            'csrfmiddlewaretoken': '{{ csrf_token }}',
            'action': 'registerPaymethod',
            'uid': uid,
            'card_name': card_name
        },
        dataType: "json",
        success: function (response) {
            if (response.result) {
                successCallback()
            } else {
                errorCallback(response.msg)
            }
        },
        error: function (request, status, error) {
            errorCallback('결제정보 등록에 실패했습니다.')
        },
    });
}
