
const plugin = new OSC.WebsocketClientPlugin({ port: 55455 })
const osc = new OSC({ plugin: plugin })
var outbox

osc.on('*', message => {
    outbox.textContent += message.address + ' ' + message.args + '\n'
})

osc.on('open', () => {
    outbox = document.getElementById("outbox")
})


osc.open()


function messageFromString(str) {
    const arr = str.split(' ')
    const path = arr[0].trim()
    const rawArgs = arr.slice(1)
    const args = []
    for (var item of rawArgs) {
        item = item.trim()
        if (item === '') continue
        args.push(toArg(item))
    }
    return new OSC.TypedMessage(path, args)
}


function toArg(item) {
    let result
    if (item === 'true') {
        result = {type: 'b', value: true }
    } else if (item === 'false') {
        result = {type: 'b', value: false }
    } else {
        const  x = Number(item)
        if (item.startsWith('\'') || item.startsWith('\"') || (x === NaN)) {
            result = {type: 's', value: item.substring(1, item.length-1)}
        } else {
            if (Number.isInteger(x)) {
                result = {type: 'i', value: parseInt(x)}
            } else {
                result = {type: 'f', value: x }
            }
        }
    }
    return result
}

function send(ele) {
    if(window.event.keyCode == 13) {
        const message = ele.value
        outbox.textContent += '> ' + message + '\n'
        osc.send(messageFromString(message))
    }
}
