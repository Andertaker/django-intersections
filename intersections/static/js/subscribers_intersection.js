$.ajaxPrefilter(function( options ) {
    options.async = false;
});



$("#group_form").submit(function(e){
    e.preventDefault();

    links = $(this).find('#id_links').val();
    links_arr = links.trim().split(/\s+/);

    $subscribers_table = $('#subscribers_table tbody');
    $subscribers_table.html('');

    var i = 0;
    iterate(i);
});


function iterate(i) {
    link = links_arr[i]

    i++;
    if (i > links_arr.length)
        return

    console.log(link);

    $.post(FETCH_GROUP_URL, {'link': link}, function(response) {
        console.log(response);
        social = response['social'];
        group = response['group'];

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
        $subscribers_table.append($row);

        if (!group['members_fetched_date']) {
            fetch_members(social, group['id'], i);
        }
        else {
            iterate(i); // iterate next link
        }
    });

}



function fetch_members(social, group_id, i) {
    url = FETCH_GROUP_MEMBERS_MONITOR_URL + social + '/' + group_id + '/'
    $cell = $subscribers_table.find('tr:last td:nth-child(3)');

    var group;

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
        if (group['members_fetched_date']) {
            clearInterval(intervalID)
            iterate(i); // iterate next link
        }
    }
    intervalID = setInterval(update_members, 5000)
    update_members(); // first start without delay
}
