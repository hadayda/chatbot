$(document).ready(function () {
    $('#chatbot_form').on('submit', function (e) {
        e.preventDefault();
        let messagesContainer = $('.messages-container');
        messagesContainer.append(
            `<li class="text-end">${$('input[name="message"]').val()}</li>`
        );
        let form = $(this)
        $.ajax({
            url: form.attr('action'),
            data: form.serialize(),
            success: function (response) {
                messagesContainer.append(
                    `<li class="text-start">${response.message}</li>`
                );
                $('input[name="message"]').val('');
            }
        })
    })
    $('input[name="message"]').on('.keypress', function (e) {
        if (e.which === 13) {
            $('#chatbot_form').submit();
        }
    });
});


function get_chat_response() {
    let form = $('#chatbot_form');

}
