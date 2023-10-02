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

const replace = () => {
    document.querySelector('#id_media').value = ''
}
