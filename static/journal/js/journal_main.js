function delMaterial() {

    var del = confirm("Вы уверены? Удалить?");
    if (del == true) {

    } else {

    }
    return del;
};

function scrollLeftFunction() {
    var elmnt = document.getElementById("inner-table");
    if (elmnt) {
        elmnt.scrollLeft += 100000;
    }
};

function loadPage() {
    scrollLeftFunction();
};

function select_all() {

    var choice = document.getElementsByName("material_choice_control")

    if (!choice[0].checked) {
        $('input[type=checkbox]').prop('checked', false);

    } else {
        $('input[type=checkbox]').prop('checked', true);

    }
};

function checkbox_selected() {
    var c = document.getElementById("id_material_choice").checked;
    if ( !c ){
        // alert("Вы НЕ выбрали ни одной записи для копирования!");
        return false;
    }
    else {
        return true;
    }

}