$(document).ready(function() {
    $('#inputForm').submit(function(e) {
        e.preventDefault();
        
        const hashtag = $('#hashtag').val();
        const numTopics = $('#numTopics').val();
        
        $('#loading').show();
        $('#results').hide();
        
        $.ajax({
            url: '/process',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ hashtag: hashtag, num_topics: numTopics }),
            success: function(response) {
                $('#loading').hide();
                if (response.error) {
                    alert('Error: ' + response.error);
                    return;
                }
                
                $('#trendsImage').attr('src', '/results/' + response.trends_image + '?' + new Date().getTime());
                $('#ldaIframe').attr('src', '/results/' + response.lda_html + '?' + new Date().getTime());
                $('#results').fadeIn();
            },
            error: function(xhr) {
                $('#loading').hide();
                alert('An error occurred: ' + xhr.responseJSON?.error || 'Unknown error');
            }
        });
    });
});