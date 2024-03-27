const color = (elements) => {
    let people = {}
    for (let i = 0; i < elements.length; i++) {
        let person = elements.item(i).innerHTML
        if (person in people) {
            elements.item(i).setAttribute("style", people[person]);
        } else {
            let random_number = Math.floor(Math.random() * 360 + 1)
            let random_color = `color :hsl(${random_number},100%,40%)`
            elements.item(i).setAttribute("style", random_color)
            people[person] = random_color;
        }
    }
}

document.body.addEventListener('htmx:load', function (evt) {
    let elements = htmx.findAll(evt.detail.elt, '.sender_name')
    color(elements)
})
document.body.addEventListener('load', function () {
    let elements = document.getElementsByClassName('sender_name')
    color(elements)
})


// let images = document.getElementsByTagName('img')
// if (images) {
//     for (let i = 0; i < images.length; i++) {
//         let image = images.item(i)
//         image.setAttribute("loading", 'lazy');
//     }
// }




const replace = () => {
    document.querySelector('#id_media').value = ''
}


const setdisplay = (form, search_button, state) => {
    if (state === 'open') {
        form.setAttribute("style", "display:flex")
        search_button.setAttribute("style", "display:none")
    } else {
        form.setAttribute("style", "display:none")
        search_button.setAttribute("style", "display:block")
    }
}