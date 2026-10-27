function toggleMenu(menuId, button) {

    const menu = document.getElementById(menuId);

    menu.classList.toggle("show");

    const arrow = button.querySelector(".arrow");

    if (arrow) {
        arrow.classList.toggle("rotate");
    }
}