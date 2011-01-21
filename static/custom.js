// shared custom code

    $(document).ready(function() {
        $('.child').click(function(event) {
            setHighlight(event.target.id);
            return false;
        });
    });
