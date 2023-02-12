const sections = document.querySelectorAll("section");

window.addEventListener("scroll", function() {
    marked_year = false;
    for (let i = 0; i < sections.length; i++) {
        const nav_id = sections[i].id;

        const rect = sections[i].getBoundingClientRect();

        if (rect.top < window.innerHeight && rect.bottom >= 80 && marked_year == false) {
            $('nav a[href="#' + nav_id + '"] h3').addClass('active');
            marked_year = true
        } else {
            $('nav a[href="#' + nav_id + '"] h3').removeClass('active');
        }
    }
});
