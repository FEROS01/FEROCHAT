const color = (elements, mode = 'light') => {
    let people = {}
    mode_object = { 'light': '40%', 'dark': '80%' }
    for (let i = 0; i < elements.length; i++) {
        let person = elements.item(i).innerHTML
        if (person in people) {
            elements.item(i).setAttribute("style", people[person]);
        } else {
            let random_number = Math.floor(Math.random() * 360 + 1)
            let random_color = `color :hsl(${random_number},100%,${mode_object[mode]})`
            elements.item(i).setAttribute("style", random_color)
            people[person] = random_color;
        }
    }
};

document.body.addEventListener('htmx:load', function (evt) {
    let elements = htmx.findAll(evt.detail.elt, '.sender_name')
    color(elements)
});
document.body.addEventListener('load', function () {
    let elements = document.getElementsByClassName('sender_name')
    color(elements)
});


// let images = document.getElementsByTagName('img')
// if (images) {
//     for (let i = 0; i < images.length; i++) {
//         let image = images.item(i)
//         image.setAttribute("loading", 'lazy');
//     }
// }




const replace = () => {
    document.querySelector('#id_media').value = ''
};


const setdisplay = (form, search_button, state) => {
    if (state === 'open') {
        form.setAttribute("style", "display:flex")
        search_button.setAttribute("style", "display:none")
    } else {
        form.setAttribute("style", "display:none")
        search_button.setAttribute("style", "display:block")
    }
};

const set_timezone = () => {
    timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone
    timezone_input = document.querySelector("[name='timezone']")
    timezone_input.value = timeZone
    htmx.trigger("#timezone", 'change')
};

const toggle_mode = () => {
    let list = document.body.classList
    let elements = document.getElementsByClassName('sender_name')
    if (list.toggle('dark')) {
        color(elements, 'dark')
    } else { color(elements) }

}
