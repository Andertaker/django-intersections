$("#group_form").submit(function(e){
    e.preventDefault();

    links = $(this).find('#id_links').val();
    links_arr = links.split(/\s+/);

    for (i in links_arr) {
        link = links_arr[i]
        console.log(link);

        $.post(FETCH_GROUP_URL, {'link': link}, function(response) {
            console.log(response);

        })

    }


})