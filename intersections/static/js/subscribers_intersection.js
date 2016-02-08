$("#group_form").submit(function(e){
    e.preventDefault();

    links = $(this).find('#id_links').val();
    links_arr = links.split(/\s+/);

    $subscribers_table = $('#subscribers_table tbody');

    for (i in links_arr) {
        link = links_arr[i]
        console.log(link);

        $.post(FETCH_GROUP_URL, {'link': link}, function(response) {
            console.log(response);
            group = response['group']

            cells_arr = [
                '<a href="%s">%s</a>'.replace(/%s/g, link),
                group['name'],
                group['members_count'],
                group['members_in_db_count'],
            ]

            cells_arr = $.map(cells_arr, function(el) {
               return $('<td>').html(el);
            });
            $row = $('<tr>').html(cells_arr);
            $subscribers_table.append($row)

            if (group['members_count'] > group['members_in_db_count']) {

            }

        })

    }


})