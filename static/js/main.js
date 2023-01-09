$(document).ready(function () {
    $('#chatbot_form').on('submit', function (e) {
        e.preventDefault();
        let messagesContainer = $('.messages-container');
        messagesContainer.append(
            `<li class="text-end mb-3 bg-primary text-white p-4 rounded-3 d-inline-block">${$('input[name="message"]').val()}</li>`
        );
        let form = $(this)
        $.ajax({
            url: form.attr('action'),
            data: form.serialize(),
            success: function (response) {
                if (response.final || false) {
                    $('.result-container').html('');
                    response.messages.forEach(function (message) {
                        $('.result-container').append(`<li class="text-start mb-3">${message}</li>`)
                    });
                    messagesContainer.html(`<li class="text-start mb-3 bg-warning p-4 rounded-3 d-inline-block">What's Your Name?</li>`);
                } else {
                    response.messages.forEach(function (message) {
                        messagesContainer.append(
                            `<li class="text-start mb-3 bg-warning p-4 rounded-3 d-inline-block">${message}</li>`
                        );
                    });
                    
                }
                messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
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
