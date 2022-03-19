display();

document.getElementById("btn").addEventListener("click", async() => {
    var rules = [];


    let new_dom = document.getElementById('new_dom').value;
    let new_s = document.getElementById('new_s').value;
    let new_r = document.getElementById('new_r').value;

    chrome.storage.sync.get(['rules'], (function(result) {
        result.rules.forEach(one_rule => {
            rules.push(one_rule);
        });
        if (new_dom != '' && new_s != '') {

            rules.push(
                [new_dom, new_s, new_r]
            );

            chrome.storage.sync.set({
                "rules": rules
            }, function() {
                console.log('Value is set to ' + String(rules));
            });

            display();
            document.getElementById('new_dom').value = '';
            document.getElementById('new_s').value = '';
            document.getElementById('new_r').value = '';
        }
    }));


});


document.getElementById("search").addEventListener("keypress", async() => {
    filter(document.getElementById("search").value);
    display();
});

function filter(text) {
    console.log('search_input onkeypress:' + text);
}

function display() {
    document.getElementById('rules').innerHTML = `
    <tr>
        <th>Domain</th>
        <th>Search</th>
        <th>Replace By</th>
    </tr>
    `;
    console.log('go');

    chrome.storage.sync.get(['rules'], function(result) {
        for (let i = 0; i < result.rules.length; i++) {
            tbodyRef = document.getElementById('rules').getElementsByTagName('tbody')[0];
            newRow = tbodyRef.insertRow(1);
            newCell1 = newRow.insertCell(0);
            newCell2 = newRow.insertCell(1);
            newCell3 = newRow.insertCell(2);
            newCell1.appendChild(document.createTextNode(result.rules[i][0]));
            newCell2.appendChild(document.createTextNode(result.rules[i][1]));
            newCell3.appendChild(document.createTextNode(result.rules[i][2]));
        }
        console.log('Starting rules: ' + result.rules);
    });


    // newCell1.appendChild(document.createTextNode(new_dom));
    // newCell2.appendChild(document.createTextNode('"' + new_s + '"'));
    // newCell3.appendChild(document.createTextNode('"' + new_r + '"'));
}