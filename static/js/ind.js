const alertButton = document.querySelector('.alert button');
if (alertButton) { alertButton.addEventListener('click', function(event) { event.preventDefault();
        alertButton.parentNode.style.display = 'none'; }, false); }