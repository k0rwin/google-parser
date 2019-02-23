$(function () {
    var timeoutId;
    var perms = {};

    function loadPerms(params) {
        clearTimeout(timeoutId);

        if (typeof params.id !== 'undefined') {
            $.ajax({
                method: 'GET',
                cache: false,
                url: "/service/",
                data: params,
                success: function (result) {
                    if (result.loaded) {
                        var perms = result.perms;
                        var html = '';

                        html += '<p class="result--title">' + result.title + '</p>';
                        html += '<p class="result--subtitle">' + result.company + '</p>';

                        html += '<div class="perms">';
                        html += '<p class="perms--title">Access to:</p>';

                        for (var i = 0; i < result.perms.length; i++) {
                            html += '<div class="perms--block">';

                            html += '<p class="perms--block--title"><img src="/icons/' + perms[i].icon + '"> <span>' + perms[i].title + '</span></p>';
                            html += '<ul class="perms--block--list">';
                            for (var p = 0; p < perms[i].perms.length; p++) {
                                html += '<li class="perms--block--item">' + perms[i].perms[p] + '</li>';
                            }
                            html += '</ul>';

                            html += '</div>';
                        }

                        html += '</div>';
                        $('#loader').hide();
                        $('#result').html(html).show();
                    } else {
                        timeoutId = setTimeout(function () {
                            loadPerms(params);
                        }, 1000);
                    }
                }
            });
        }
    }

    function initLoading() {
        $('#result').hide();
        $('#loader').show();
        var link = $('#link').val();
        var a = document.createElement('a');
        a.href = link;
        var search = a.search.substr(1);
        var ar = search.split('&');
        var params = {};
        ar.map(function (item) {
            var key, value;
            [key, value] = item.split('=');
            params[key] = value;
        });

        loadPerms(params);
    }

    $('#load').on('click', function () {
        initLoading();
    });

    $('#form').on('submit', function () {
        initLoading();
        return false;
    });
});
