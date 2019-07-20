let jewels = {}

$(function () {
    if (window.File && window.FileReader && window.FileList && window.Blob) {
        // File API works
    } else {
        alert('The File APIs are not fully supported in this browser.');
    }

    $('#jsonFiles').change(function () {
        const files = document.getElementById("jsonFiles").files;

        for (var i = 0, f; f = files[i]; i++) {
            if (!f.type.match('application/json')) {
                continue;
            }

            const reader = new FileReader();

            reader.onload = (function (file) {
                return function (e) {
                    jsonEncoded = e.target.result.split(",")[1]
                    json = JSON.parse(atob(jsonEncoded))
                    if(!jewels.hasOwnProperty(file.name)) {
                        $("#jewelsTable").append(`
                        <tr>
                            <td><a href="javascript:;" onclick="changeTable('${file.name}')">${json.info.type}</a></td>
                            <td>${json.info.seed}</td>
                            <td>${json.info.variant}</td>
                            <td>${json.info.socket.name} <span class="node-type">(ID: ${json.info.socket.index})</span></td>
                        </tr>
                        `)
                    }
                    jewels[file.name] = json // Update json
                };
            })(f);

            reader.readAsDataURL(f);
        }
    });
});

$("#jsonSelect").click(function () {
    $("#jsonFiles").click();
});

function changeTable(file) {
    let json = jewels[file];

    $(".jewel-info .name").html(`${json.info.type}<br />`)
    $(".jewel-info .info").html(`Seed ${json.info.seed}, ${json.info.variant}, ${json.info.socket.name} <span class="node-type">(ID: ${json.info.socket.index})</span>`)

    $("#jewelNodes").empty()
    drawNodes(json["nodes"])
    for (const nodeIndex in json["nodes"]) {
        const node = json["nodes"][nodeIndex]

        row = `<tr>`

        if(node.passives.original.every(v => node.passives.new.includes(v))) {
            row += `<td><span class="new-name">${node.name.new}</span> <span class="node-type">(${node.type})</span><br />
                    ${node.passives.original.join("<br />")}<br /><span class="added-mod">${node.passives.added.join("<br />")}</span></td>`
        } else {
            row += `<td><span class="new-name">${node.name.new}</span> <span class="node-type">(${node.type})</span><br />
                    <span class="added-mod">${node.passives.new.join("<br />")}</span></td>`
        }

        row += `<td><span class="original-name">${node.name.original}</span> <span class="node-type">(${node.type})</span><br />
                ${node.passives.original.join("<br />")}</td></tr>`
        $("#jewelNodes").append(row)
    }
}

function drawNodes(nodes) {
    const canvas = $("#canvas");
    canvas.show()
    const ctx = canvas[0].getContext("2d");

    const shrinkFactor = 2.5
    const notableSize = parseInt(14 / shrinkFactor)
    const regularSize = parseInt(9 / shrinkFactor)
    
    const w = parseInt($("#selector").width() / shrinkFactor);
    canvas.attr("height", w + 'px');
    canvas.attr("width", w + 'px');

    const center = parseInt(canvas.width() / 2)

    ctx.beginPath();
    ctx.arc(center, center, notableSize, 0, 2 * Math.PI);
    ctx.fillStyle = "#f05f33";
    ctx.fill();

    ctx.beginPath();
    ctx.arc(center, center, center, 0, 2 * Math.PI);
    ctx.strokeStyle = "lightgrey";
    ctx.stroke();

    console.log(nodes)
    for(const nodeIndex in nodes) {
        node = nodes[nodeIndex]
        x = parseInt(center + (node["x"] * center))
        y = parseInt(center + (node["y"] * center))

        radius = regularSize
        fillStyle = "grey"
        if(node["type"] == "notable") {
            radius = notableSize
            fillStyle = "#33C3F0"
        }

        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        ctx.fillStyle = fillStyle;
        ctx.fill();
    }
}