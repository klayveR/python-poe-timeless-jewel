let jewels = {}

$(function () {
    if (window.File && window.FileReader && window.FileList && window.Blob) {
        // Great success! All the File APIs are supported.
    } else {
        alert('The File APIs are not fully supported in this browser.');
    }

    $('#jsonFiles').change(function () {
        const files = document.getElementById("jsonFiles").files; // FileList object

        // Loop through the FileList and render image files as thumbnails.
        for (var i = 0, f; f = files[i]; i++) {
            if (!f.type.match('application/json')) {
                continue;
            }

            const reader = new FileReader();

            // Closure to capture the file information.
            reader.onload = (function (file) {
                return function (e) {
                    jsonEncoded = e.target.result.split(",")[1]
                    json = JSON.parse(atob(jsonEncoded))
                    if(!jewels.hasOwnProperty(file.name)) {
                        jewels[file.name] = json
                        $("#jewelsTable").append(`
                        <tr>
                            <td><a href="javascript:;" onclick="changeTable('${file.name}')">${json.info.type}</a></td>
                            <td>${json.info.seed}</td>
                            <td>${json.info.variant}</td>
                            <td>${json.info.socket.name} (${json.info.socket.index})</td>
                        </tr>
                        `)
                    }
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
    $(".jewel-info .info").html(`Seed ${json.info.seed}, ${json.info.variant}, ${json.info.socket.name} (${json.info.socket.index})`)

    $("#jewelNodes").empty()
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