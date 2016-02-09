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
                group['members_in_db_count'],
                group['members_count'],
            ]

            cells_arr = $.map(cells_arr, function(el) {
               return $('<td>').html(el);
            });
            $row = $('<tr>').html(cells_arr);
            $subscribers_table.append($row)

            if (!group['members_fetched_date']) {
                fetch_members(response['social'], group['id']);
            }

        });

    }
});



function fetch_members(social, group_id) {
    url = FETCH_GROUP_MEMBERS_MONITOR_URL + social + '/' + group_id + '/'
    $cell = $subscribers_table.find('tr:last td:nth-child(3)');

    settings = {
        'url': url,
        'async': false,
        'success': function(response) {
            group = response['group'];
            $cell.html(group['members_in_db_count']);
        }
    }

    update_members = function(){
        $.get(settings);
        if (group['members_fetched_date'])
            clearInterval(intervalID)
    }
    intervalID = setInterval(update_members, 5000)
    update_members(); // first start without delay

}




