$(function () {
  // Initialization of the "You need to be authenticated" tooltips
  $('a[data-toggle="tooltip"]').tooltip();
  // Handling "+" and "-" vote links
  $('a[data-url]').click(function (event) {
    var target = $(event.currentTarget);
    var url = target.attr('data-url');
    var postId = target.attr('data-postid');
    var csrf = $('[name="csrfmiddlewaretoken"]').val();
    $.post({
      url: url,
      headers: {
        'X-CSRFToken': csrf,
      },
      success: function (data) {
        var up = $(`a[data-postid="${postId}"][data-direction="up"]`);
        var down = $(`a[data-postid="${postId}"][data-direction="down"]`);
        var rating = $(`span[data-postid="${postId}"]`);
        rating.text(1 * rating.text() + data.change);
        switch (data.vote) {
          case null:
            up.attr('class', 'text-dark');
            down.attr('class', 'text-dark');
            break;
          case true:
            up.attr('class', 'text-warning');
            down.attr('class', 'text-dark');
            break;
          case false:
            up.attr('class', 'text-dark');
            down.attr('class', 'text-warning');
            break;
        };
      },
      error: function (xhr, status, error) {
        console.log(error);
      }
    });
  });
});
