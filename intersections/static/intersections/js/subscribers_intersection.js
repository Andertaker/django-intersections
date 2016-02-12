$.ajaxPrefilter(function( options ) {
    options.async = false;
});



var intervalID;
var groups;


$("#group_form").submit(function(e){
    e.preventDefault();

    if (intervalID)
        clearInterval(intervalID)

    links = $(this).find('#id_links').val();
    links_arr = links.trim().split(/\s+/);

    $subscribers_table = $('#subscribers_table').show();
    $subscribers_table = $('#subscribers_table').find('tbody');
    $subscribers_table.html('');

    $intersections_tbody = $('#intersections_table tbody');
    $intersections_tbody.html('');
    $intersections_thead = $('#intersections_table thead');
    $intersections_thead.html('<tr><th>ПЕРЕСЕЧЕНИЕ</th><th></th></tr><tr><th></th><th></th></tr>');

    groups = [];
    var i = 0;
    iterate(i);
});





function iterate(i) {
    link = links_arr[i];

    i++;
    if (i > links_arr.length)
        return

    $.post(FETCH_GROUP_URL, {'link': link}, function(response) {
        if (response['errors']) {
            $row = $('<tr>');
            $cell1 = $('<td>').html(link).appendTo($row);
            $cell2 = $('<td class="error" colspan=3>').html(response['errors']).appendTo($row);
            $subscribers_table.append($row);
            iterate(i); // iterate next link
            return
        }

        social = response['social'];
        group = response['group'];

        var members_in_db_count = group['members_in_db_count'];
        if (!group['members_fetched_date']) {
            members_in_db_count += '<i class="progress"> ...</i>';
        }

        cells_arr = [
            '<a href="%s">%s</a>'.replace(/%s/g, link),
            group['name'],
            members_in_db_count,
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
            groups.push(group);
            generate_intersections_table();
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

            var members_in_db_count = group['members_in_db_count'];
            if (!group['members_fetched_date']) {
                members_in_db_count += '<i class="progress"> ...</i>';
            }

            $cell.html(members_in_db_count);
        }
    }

    update_members = function(){
        $.get(settings);
        if (group['members_fetched_date']) {
            clearInterval(intervalID);
            groups.push(group);
            generate_intersections_table();
            iterate(i); // iterate next link
        }
    }
    intervalID = setInterval(update_members, 5000);
    update_members(); // first start without delay
}


function generate_intersections_table() {
    group = groups[groups.length-1] // last group

    // thead
    $row1 = $intersections_thead.find('tr:first');
    $row2 = $intersections_thead.find('tr:last');

    $cell1 = $('<th>').html(group['screen_name'])
    $cell2 = $('<td>').html(group['members_in_db_count'])
    $cell1.appendTo($row1);
    $cell2.appendTo($row2);

    // tbody
    $row = $('<tr>').appendTo($intersections_tbody); // last row
    $cell1 = $('<th>').html(group['screen_name'])
    $cell2 = $('<td>').html(group['members_in_db_count'])
    $cell1.appendTo($row);
    $cell2.appendTo($row);

    // intersections
    for(var i = 0; i < groups.length - 1; i++) {
        var group1 = groups[i];

        url = GET_INTERSECTIONS_URL + group1['id'] + '/' + group['id'] + '/';
        $.get(url, function(response) {
            $cell = $('<th>').html(response['intersections_count'])
            $cell.appendTo($row);
        });
    }

    // add_epty_cells_to_rows
    var cells_count = $intersections_thead.find('tr:first th').length;

    $intersections_tbody.find('tr').each(function(index){
        var cells_in_row = $(this).find('th').length;

        for(cells_in_row; cells_in_row < cells_count - 1; cells_in_row++) {
            $('<th>').appendTo($(this));
        }
    });
}
